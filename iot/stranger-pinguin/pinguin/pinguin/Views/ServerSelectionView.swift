//
//  ServerSelectionView.swift
//  pinguin
//
//  Server selection screen shown at app launch
//

import SwiftUI

struct ServerSelectionView: View {
    @Binding var selectedMode: ServerMode?
    
    var body: some View {
        ZStack {
            // Background gradient
            LinearGradient(
                colors: [Color(hex: "1a1a2e"), Color(hex: "16213e")],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()
            
            VStack(spacing: 40) {
                // Logo/Title
                VStack(spacing: 12) {
                    Image(systemName: "waveform.circle.fill")
                        .font(.system(size: 80))
                        .foregroundStyle(.white.opacity(0.9))
                    
                    Text("PINGUIN")
                        .font(.system(size: 32, weight: .black, design: .monospaced))
                        .foregroundStyle(.white)
                        .tracking(8)
                    
                    Text("Sélectionnez votre mode")
                        .font(.system(size: 14, weight: .medium))
                        .foregroundStyle(.white.opacity(0.6))
                }
                .padding(.top, 60)
                
                Spacer()
                
                // Server Mode Cards
                VStack(spacing: 20) {
                    ServerModeCard(
                        mode: .cosmo,
                        icon: "sun.max.fill",
                        color: .orange,
                        description: "Mode standard"
                    ) {
                        withAnimation(.spring(response: 0.4, dampingFraction: 0.7)) {
                            selectedMode = .cosmo
                        }
                    }
                    .accessibilityIdentifier("cosmoCard")
                    
                    ServerModeCard(
                        mode: .darkCosmo,
                        icon: "moon.fill",
                        color: .purple,
                        description: "Mode alternatif"
                    ) {
                        withAnimation(.spring(response: 0.4, dampingFraction: 0.7)) {
                            selectedMode = .darkCosmo
                        }
                    }
                    .accessibilityIdentifier("darkCosmoCard")
                }
                .padding(.horizontal, 32)
                
                Spacer()
                
                // Footer
                Text("Port: 8000 (Cosmo) • 8001 (Dark Cosmo)")
                    .font(.system(size: 11, design: .monospaced))
                    .foregroundStyle(.white.opacity(0.3))
                    .padding(.bottom, 40)
            }
        }
    }
}

struct ServerModeCard: View {
    let mode: ServerMode
    let icon: String
    let color: Color
    let description: String
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 20) {
                // Icon
                ZStack {
                    Circle()
                        .fill(color.opacity(0.2))
                        .frame(width: 60, height: 60)
                    
                    Image(systemName: icon)
                        .font(.system(size: 26))
                        .foregroundStyle(color)
                }
                
                // Text
                VStack(alignment: .leading, spacing: 4) {
                    Text(mode.displayName)
                        .font(.system(size: 20, weight: .bold))
                        .foregroundStyle(.white)
                    
                    Text(description)
                        .font(.system(size: 13, weight: .medium))
                        .foregroundStyle(.white.opacity(0.5))
                    
                    Text("Port \(mode.port)")
                        .font(.system(size: 11, weight: .medium, design: .monospaced))
                        .foregroundStyle(color.opacity(0.8))
                }
                
                Spacer()
                
                // Arrow
                Image(systemName: "chevron.right")
                    .font(.system(size: 18, weight: .semibold))
                    .foregroundStyle(.white.opacity(0.3))
            }
            .padding(20)
            .background(
                RoundedRectangle(cornerRadius: 20)
                    .fill(.white.opacity(0.08))
                    .overlay(
                        RoundedRectangle(cornerRadius: 20)
                            .strokeBorder(.white.opacity(0.1), lineWidth: 1)
                    )
            )
        }
        .buttonStyle(ScaleButtonStyle())
    }
}

struct ScaleButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed ? 0.97 : 1.0)
            .animation(.spring(response: 0.2), value: configuration.isPressed)
    }
}

#Preview {
    ServerSelectionView(selectedMode: .constant(nil))
}
