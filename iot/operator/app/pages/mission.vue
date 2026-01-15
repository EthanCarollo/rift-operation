<template>
  <div class="mission-dashboard">
    <!-- Corner Decorations -->
    <div class="corner corner-tl"></div>
    <div class="corner corner-tr"></div>
    <div class="corner corner-bl"></div>
    <div class="corner corner-br"></div>

    <!-- Header Bar -->
    <header class="mission-header">
      <div class="header-content">
        <div class="header-title">
          <span class="logo-r">R</span>
          <span class="logo-text">MISSION: RIFT OPERATION</span>
        </div>
        <div class="header-divider"></div>
        <span class="header-time">09:08:04</span>
        <span class="header-date">Jan 21, 2026</span>
      </div>
    </header>

    <!-- Main Content Grid -->
    <main class="mission-content">
      <!-- Left Column -->
      <div class="left-column">
        <!-- Mission Briefing -->
        <section class="panel mission-briefing">
          <div class="panel-header">
            <div class="panel-title">
              <svg class="panel-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 16v-4M12 8h.01"/>
              </svg>
              <span>BRIEFING DE MISSION</span>
            </div>
            <div class="status-indicators">
              <span class="status-badge">OP-3847</span>
              <span class="priority-badge">PRIORITÉ 1</span>
            </div>
          </div>
          <div class="briefing-content">
            <p class="mission-objective">Monde 1 : Identifier le prénom de l'étranger en collaborant entre les différents mondes</p>
          </div>
        </section>

        <!-- Mission Progress -->
        <section class="panel mission-progress">
          <div class="panel-header">
            <span class="panel-title-text">AVANCÉE DE LA MISSION</span>
          </div>
          <div class="stats-grid">
            <div class="stat-box">
              <span class="stat-value">01:33</span>
              <span class="stat-label">Temps passé dans la faille</span>
            </div>
            <div class="stat-box">
              <span class="stat-value">2</span>
              <span class="stat-label">Morceaux de faille récupérés</span>
            </div>
            <div class="stat-box">
              <span class="stat-value">4</span>
              <span class="stat-label">Morceaux de faille restants</span>
            </div>
            <div class="stat-box">
              <span class="stat-value">2,50m</span>
              <span class="stat-label">Largeur de la faille</span>
            </div>
          </div>
        </section>
      </div>

      <!-- Middle Column -->
      <div class="middle-column">
        <!-- Fault Monitor -->
        <section class="panel fault-monitor">
          <div class="panel-header">
            <span class="panel-title-text">MONITEUR DE FAILLE</span>
          </div>
          <div class="progress-section">
            <div class="progress-header">
              <span>Étape 1/3</span>
              <span>33.33%</span>
            </div>
            <div class="progress-bar-container">
              <div class="progress-bar" style="width: 33.33%;"></div>
            </div>
          </div>
          <div class="fault-visualization">
            <div class="fault-graphic">
              <!-- Abstract fault visualization -->
              <svg viewBox="0 0 300 200" class="fault-svg">
                <polygon points="150,20 200,80 180,120 220,180 150,140 80,180 120,120 100,80" 
                         fill="var(--mission-yellow)" 
                         stroke="var(--mission-accent)" 
                         stroke-width="2"/>
                <polygon points="150,40 180,90 160,120 190,160 150,130 110,160 140,120 120,90" 
                         fill="var(--mission-accent)" 
                         opacity="0.6"/>
              </svg>
            </div>
          </div>
        </section>
      </div>

      <!-- Right Column -->
      <div class="right-column">
        <!-- Agent Dashboard -->
        <section class="panel agent-dashboard">
          <div class="panel-header">
            <span class="panel-title-text">TABLEAU DE BORD AGENT</span>
          </div>
          <div class="dashboard-content">
            <!-- Map Section -->
            <div class="map-section">
              <div class="map-labels">
                <span>ZONE RÊVE</span>
                <span>ZONE CAUCHEMAR</span>
              </div>
              <div class="map-visual">
                <div class="divider-line"></div>
                <div class="agent-marker agent-1">
                  <div class="marker-dot"></div>
                  <span>Agent 1</span>
                </div>
                <div class="agent-marker agent-2">
                  <div class="marker-dot marker-pink"></div>
                  <span>Agent 2</span>
                </div>
              </div>
            </div>
            <!-- Agent Cards -->
            <div class="agent-cards">
              <div class="agent-card">
                <div class="agent-avatar">
                  <div class="avatar-circle"></div>
                </div>
                <div class="agent-info">
                  <span class="agent-name">Agent 1</span>
                  <span class="agent-role">Navigateur Onirique</span>
                  <span class="agent-status online">● En Mission</span>
                </div>
                <div class="agent-stats">
                  <div class="stat-bar">
                    <span class="stat-icon">♥</span>
                    <div class="bar-bg"><div class="bar-fill" style="width: 92%;"></div></div>
                    <span class="stat-percent">92%</span>
                  </div>
                  <div class="stat-bar">
                    <span class="stat-icon">⚡</span>
                    <div class="bar-bg"><div class="bar-fill" style="width: 87%;"></div></div>
                    <span class="stat-percent">87%</span>
                  </div>
                </div>
              </div>
              <div class="agent-card">
                <div class="agent-avatar">
                  <div class="avatar-circle avatar-pink"></div>
                </div>
                <div class="agent-info">
                  <span class="agent-name">Agent 2</span>
                  <span class="agent-role">Chasseur de Cauchemars</span>
                  <span class="agent-status online">● En Mission</span>
                </div>
                <div class="agent-stats">
                  <div class="stat-bar">
                    <span class="stat-icon">♥</span>
                    <div class="bar-bg"><div class="bar-fill bar-pink" style="width: 93%;"></div></div>
                    <span class="stat-percent">93%</span>
                  </div>
                  <div class="stat-bar">
                    <span class="stat-icon">⚡</span>
                    <div class="bar-bg"><div class="bar-fill bar-pink" style="width: 87%;"></div></div>
                    <span class="stat-percent">87%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Communication Flux -->
        <section class="panel communication-flux">
          <div class="panel-header">
            <div class="panel-title">
              <span class="wifi-icon">((•))</span>
              <span>FLUX DE COMMUNICATION</span>
            </div>
            <span class="live-badge">● DIRECT</span>
          </div>
          <div class="messages-list">
            <div class="message">
              <div class="message-header">
                <span class="message-agent">AGENT-02</span>
                <span class="message-time">14:23:15</span>
              </div>
              <p class="message-content">Fragment trouvé derrière la banquise !</p>
            </div>
            <div class="message">
              <div class="message-header">
                <span class="message-agent">AGENT-02</span>
                <span class="message-time">14:23:42</span>
              </div>
              <p class="message-content">Homme inconnu qui hante le cauchemars détectée</p>
            </div>
            <div class="message">
              <div class="message-header">
                <span class="message-agent agent-green">AGENT-01</span>
                <span class="message-time">14:24:31</span>
              </div>
              <p class="message-content">Question 3 résolu grâce à Cosmo</p>
            </div>
            <div class="message">
              <div class="message-header">
                <span class="message-agent agent-green">AGENT-01</span>
                <span class="message-time">14:24:08</span>
              </div>
              <p class="message-content">Question 1 trouvée</p>
            </div>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
// No logic needed - this is a display-only page
</script>

<style scoped>
.mission-dashboard {
  min-height: 100vh;
  width: 100%;
  background: linear-gradient(to right, var(--mission-bg), var(--mission-bg));
  position: relative;
  font-family: 'Inter', 'Space Mono', sans-serif;
  color: var(--mission-text);
  overflow: hidden;
}

/* Corner Decorations */
.corner {
  position: absolute;
  width: 144px;
  height: 144px;
  opacity: 0.5;
  pointer-events: none;
  z-index: 10;
}
.corner-tl { top: 0; left: 0; border-left: 2px solid var(--mission-accent); border-top: 2px solid var(--mission-accent); }
.corner-tr { top: 0; right: 0; border-right: 2px solid var(--mission-accent); border-top: 2px solid var(--mission-accent); }
.corner-bl { bottom: 0; left: 0; border-left: 2px solid var(--mission-accent); border-bottom: 2px solid var(--mission-accent); }
.corner-br { bottom: 0; right: 0; border-right: 2px solid var(--mission-accent); border-bottom: 2px solid var(--mission-accent); }

/* Header */
.mission-header {
  position: absolute;
  top: 12px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 20;
}
.header-content {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 16px 24px;
  background: rgba(0, 255, 196, 0.05);
  border: 1px solid rgba(0, 255, 196, 0.3);
  border-radius: 4px;
}
.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
}
.logo-r {
  font-size: 24px;
  font-weight: bold;
  color: var(--mission-accent);
}
.logo-text {
  font-size: 20px;
  font-weight: 600;
  color: var(--mission-accent);
  letter-spacing: 1px;
}
.header-divider {
  width: 2px;
  height: 27px;
  background: rgba(0, 255, 196, 0.4);
}
.header-time {
  font-size: 20px;
  color: var(--mission-accent);
}
.header-date {
  font-size: 20px;
  color: rgba(204, 255, 255, 0.6);
}

/* Main Content */
.mission-content {
  display: grid;
  grid-template-columns: 1fr 1.2fr 1.3fr;
  gap: 16px;
  padding: 92px 16px 16px;
  height: 100vh;
  box-sizing: border-box;
}

.left-column, .middle-column, .right-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Panels */
.panel {
  background: rgba(0, 255, 196, 0.02);
  border: 1px solid rgba(0, 255, 196, 0.3);
  border-radius: 4px;
  padding: 16px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--mission-accent);
  font-size: 14px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.panel-title-text {
  color: var(--mission-accent);
  font-size: 14px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.panel-icon {
  width: 24px;
  height: 24px;
  color: var(--mission-accent);
}

.status-indicators {
  display: flex;
  gap: 8px;
}

.status-badge {
  padding: 4px 8px;
  background: rgba(0, 255, 196, 0.1);
  border: 1px solid var(--mission-accent);
  color: var(--mission-accent);
  font-size: 11px;
  border-radius: 2px;
}

.priority-badge {
  padding: 4px 8px;
  background: rgba(255, 0, 0, 0.2);
  border: 1px solid #ff4444;
  color: #ff4444;
  font-size: 11px;
  border-radius: 2px;
}

/* Mission Briefing */
.mission-briefing {
  flex: 1;
}
.briefing-content {
  flex: 1;
  display: flex;
  align-items: center;
}
.mission-objective {
  font-size: 28px;
  font-weight: 600;
  color: var(--mission-yellow);
  line-height: 1.4;
}

/* Mission Progress */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.stat-box {
  background: rgba(0, 255, 196, 0.05);
  border: 1px solid rgba(0, 255, 196, 0.2);
  padding: 16px;
  text-align: center;
  border-radius: 4px;
}
.stat-value {
  display: block;
  font-size: 36px;
  font-weight: 700;
  color: var(--mission-accent);
  margin-bottom: 8px;
}
.stat-label {
  font-size: 11px;
  color: rgba(204, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Fault Monitor */
.fault-monitor {
  flex: 1;
}
.progress-section {
  margin-bottom: 20px;
}
.progress-header {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: var(--mission-text);
  margin-bottom: 8px;
}
.progress-bar-container {
  height: 8px;
  background: rgba(0, 255, 196, 0.1);
  border-radius: 4px;
  overflow: hidden;
}
.progress-bar {
  height: 100%;
  background: linear-gradient(to right, var(--mission-accent), var(--mission-yellow));
  border-radius: 4px;
  transition: width 0.3s ease;
}
.fault-visualization {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}
.fault-graphic {
  width: 100%;
  max-width: 300px;
}
.fault-svg {
  width: 100%;
  height: auto;
}

/* Agent Dashboard */
.agent-dashboard {
  flex: 1;
}
.dashboard-content {
  display: flex;
  gap: 20px;
  height: calc(100% - 50px);
}
.map-section {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.map-labels {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: rgba(204, 255, 255, 0.6);
  text-transform: uppercase;
  margin-bottom: 12px;
}
.map-visual {
  flex: 1;
  position: relative;
  background: rgba(0, 255, 196, 0.02);
  border: 1px solid rgba(0, 255, 196, 0.15);
  border-radius: 4px;
  min-height: 150px;
}
.divider-line {
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0;
  width: 2px;
  background: linear-gradient(to bottom, transparent, var(--mission-accent), transparent);
}
.agent-marker {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  color: var(--mission-text);
}
.agent-1 { left: 25%; top: 40%; }
.agent-2 { left: 70%; top: 60%; }
.marker-dot {
  width: 24px;
  height: 24px;
  background: var(--mission-accent);
  border-radius: 50%;
  box-shadow: 0 0 15px var(--mission-accent);
}
.marker-pink {
  background: var(--mission-pink);
  box-shadow: 0 0 15px var(--mission-pink);
}

/* Agent Cards */
.agent-cards {
  width: 220px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.agent-card {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: rgba(0, 255, 196, 0.03);
  border: 1px solid rgba(0, 255, 196, 0.15);
  border-radius: 4px;
}
.agent-avatar {
  flex-shrink: 0;
}
.avatar-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--mission-accent), transparent);
  border: 2px solid var(--mission-accent);
}
.avatar-pink {
  background: linear-gradient(135deg, var(--mission-pink), transparent);
  border-color: var(--mission-pink);
}
.agent-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}
.agent-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--mission-text);
}
.agent-role {
  font-size: 10px;
  color: rgba(204, 255, 255, 0.5);
}
.agent-status {
  font-size: 10px;
}
.agent-status.online {
  color: var(--mission-accent);
}
.agent-stats {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: auto;
}
.stat-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 10px;
}
.stat-icon {
  color: var(--mission-accent);
  width: 12px;
}
.bar-bg {
  flex: 1;
  height: 4px;
  background: rgba(0, 255, 196, 0.1);
  border-radius: 2px;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  background: var(--mission-accent);
  border-radius: 2px;
}
.bar-pink {
  background: var(--mission-pink);
}
.stat-percent {
  color: rgba(204, 255, 255, 0.6);
  width: 28px;
  text-align: right;
}

/* Communication Flux */
.communication-flux {
  flex: 1;
}
.wifi-icon {
  color: var(--mission-accent);
  font-weight: bold;
}
.live-badge {
  color: #ff4444;
  font-size: 12px;
  font-weight: 600;
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
.messages-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 300px;
  overflow-y: auto;
}
.message {
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(0, 255, 196, 0.1);
}
.message:last-child {
  border-bottom: none;
}
.message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}
.message-agent {
  font-size: 12px;
  font-weight: 600;
  color: var(--mission-pink);
}
.message-agent.agent-green {
  color: var(--mission-accent);
}
.message-time {
  font-size: 11px;
  color: rgba(204, 255, 255, 0.4);
}
.message-content {
  font-size: 13px;
  color: var(--mission-text);
  line-height: 1.4;
  margin: 0;
}

/* Scrollbar Styling */
.messages-list::-webkit-scrollbar {
  width: 4px;
}
.messages-list::-webkit-scrollbar-track {
  background: rgba(0, 255, 196, 0.05);
}
.messages-list::-webkit-scrollbar-thumb {
  background: var(--mission-accent);
  border-radius: 2px;
}
</style>
