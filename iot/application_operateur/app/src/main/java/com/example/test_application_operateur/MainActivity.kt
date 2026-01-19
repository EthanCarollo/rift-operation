package com.example.test_application_operateur

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.view.MotionEvent
import android.view.View
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import com.example.test_application_operateur.databinding.ActivityMainBinding
import java.net.Inet4Address
import java.net.NetworkInterface

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var liveKit: LiveKitManager
    private var isConnected = false

    private val permissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) Toast.makeText(this, "OK", Toast.LENGTH_SHORT).show()
        else Toast.makeText(this, "Permission micro requise!", Toast.LENGTH_LONG).show()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        liveKit = LiveKitManager(this)
        
        setupUI()
        requestPermission()
        showLocalIp()
        
        // Pre-fill server IP
        binding.serverIpInput.setText("192.168.10.4")
    }

    override fun onDestroy() {
        super.onDestroy()
        liveKit.disconnect()
    }

    private fun setupUI() {
        // Sélection du rôle
        binding.roleGroup.setOnCheckedChangeListener { _, id ->
            when (id) {
                R.id.roleB -> {
                    liveKit.role = LiveKitManager.Role.OPERATOR_B
                    binding.serverIpContainer.visibility = View.VISIBLE
                    binding.buttonContainer.visibility = View.VISIBLE
                    binding.channelIndicator.visibility = View.VISIBLE
                    binding.title.text = "📱 OPÉRATEUR B (LiveKit)"
                }
                R.id.roleA -> {
                    liveKit.role = LiveKitManager.Role.CLIENT_A
                    binding.serverIpContainer.visibility = View.VISIBLE
                    binding.buttonContainer.visibility = View.GONE
                    binding.channelIndicator.visibility = View.GONE
                    binding.title.text = "📱 CLIENT A (LiveKit)"
                }
                R.id.roleC -> {
                    liveKit.role = LiveKitManager.Role.CLIENT_C
                    binding.serverIpContainer.visibility = View.VISIBLE
                    binding.buttonContainer.visibility = View.GONE
                    binding.channelIndicator.visibility = View.GONE
                    binding.title.text = "📱 CLIENT C (LiveKit)"
                }
            }
        }
        
        // Bouton Start/Stop
        binding.fabStartStop.setOnClickListener {
            if (isConnected) disconnect() else connect()
        }

        // Boutons L/R (push-to-talk)
        binding.btnLeft.setOnTouchListener { v, e -> handleButton(v, e, LiveKitManager.Channel.LEFT) }
        binding.btnRight.setOnTouchListener { v, e -> handleButton(v, e, LiveKitManager.Channel.RIGHT) }

        // Callbacks
        liveKit.onStatus = { runOnUiThread { binding.statusText.text = it } }
        liveKit.onMicLevel = { runOnUiThread { binding.vuMeter.progress = it } }
        liveKit.onRemoteLevel = { runOnUiThread { binding.vuMeterRemote.progress = it } }
        liveKit.onParticipantJoined = { identity ->
            runOnUiThread {
                Toast.makeText(this, "$identity connecté!", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun handleButton(v: View, e: MotionEvent, ch: LiveKitManager.Channel): Boolean {
        if (!isConnected) return true
        when (e.action) {
            MotionEvent.ACTION_DOWN -> {
                liveKit.setChannel(ch)
                v.isPressed = true
                updateChannelText()
            }
            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                liveKit.setChannel(LiveKitManager.Channel.NONE)
                v.isPressed = false
                updateChannelText()
            }
        }
        return true
    }

    private fun connect() {
        if (!hasPermission()) {
            requestPermission()
            return
        }
        
        val ip = binding.serverIpInput.text.toString().trim()
        if (ip.isEmpty()) {
            Toast.makeText(this, "Entrez l'IP du serveur", Toast.LENGTH_SHORT).show()
            return
        }
        
        liveKit.serverUrl = "ws://$ip:7880"
        
        if (liveKit.connect()) {
            isConnected = true
            binding.fabStartStop.setImageResource(android.R.drawable.ic_media_pause)
            binding.btnLeft.isEnabled = liveKit.role == LiveKitManager.Role.OPERATOR_B
            binding.btnRight.isEnabled = liveKit.role == LiveKitManager.Role.OPERATOR_B
            setUIEnabled(false)
            updateChannelText()
        } else {
            Toast.makeText(this, "Erreur connexion", Toast.LENGTH_SHORT).show()
        }
    }

    private fun disconnect() {
        liveKit.disconnect()
        isConnected = false
        binding.fabStartStop.setImageResource(android.R.drawable.ic_media_play)
        binding.vuMeter.progress = 0
        binding.vuMeterRemote.progress = 0
        binding.btnLeft.isEnabled = false
        binding.btnRight.isEnabled = false
        setUIEnabled(true)
        updateChannelText()
    }

    private fun setUIEnabled(enabled: Boolean) {
        binding.roleB.isEnabled = enabled
        binding.roleA.isEnabled = enabled
        binding.roleC.isEnabled = enabled
        binding.serverIpInput.isEnabled = enabled
    }

    private fun updateChannelText() {
        binding.channelIndicator.text = when {
            !isConnected -> "⏸️ Déconnecté"
            liveKit.currentChannel == LiveKitManager.Channel.LEFT -> "👈 PARLE À A"
            liveKit.currentChannel == LiveKitManager.Channel.RIGHT -> "👉 PARLE À C"
            else -> "🔇 Appuie pour parler"
        }
    }

    private fun showLocalIp() {
        try {
            NetworkInterface.getNetworkInterfaces()?.toList()?.forEach { iface ->
                iface.inetAddresses?.toList()?.forEach { addr ->
                    if (!addr.isLoopbackAddress && addr is Inet4Address) {
                        binding.localIp.text = "Mon IP: ${addr.hostAddress}"
                        return
                    }
                }
            }
        } catch (e: Exception) { }
        binding.localIp.text = "Mon IP: ?"
    }

    private fun hasPermission() = ContextCompat.checkSelfPermission(
        this, Manifest.permission.RECORD_AUDIO
    ) == PackageManager.PERMISSION_GRANTED

    private fun requestPermission() {
        if (!hasPermission()) {
            permissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
        }
    }
}
