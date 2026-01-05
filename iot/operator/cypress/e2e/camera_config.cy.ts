/// <reference types="cypress" />

describe('Camera Config and Filters', () => {
  beforeEach(() => {
    // Mock navigator.mediaDevices
    cy.visit('/config', {
      onBeforeLoad(win) {
        cy.stub(win.navigator.mediaDevices, 'enumerateDevices').resolves([
          { deviceId: 'cam1', kind: 'videoinput', label: 'Camera 1' },
          { deviceId: 'cam2', kind: 'videoinput', label: 'Camera 2' },
        ])
        cy.stub(win.navigator.mediaDevices, 'getUserMedia').callsFake(() => {
            return Promise.resolve(new win.MediaStream())
        })
      },
    })
  })

  it('allows selecting a camera and renaming it', () => {
    // Check if cameras are rendered
    cy.get('video').should('have.length', 2)
    
    // Select first camera
    cy.get('video').first().click({ force: true })
    
    // Check for input field
    cy.get('input[placeholder="ENTER DESIGNATOR"]').should('be.visible')
    
    // Type name (split clear and type to avoid detached DOM)
    cy.get('input[placeholder="ENTER DESIGNATOR"]').clear()
    cy.get('input[placeholder="ENTER DESIGNATOR"]').type('TEST_CAM_01')
    
    // Verify selection indicator
    cy.get('input[placeholder="ENTER DESIGNATOR"]').should('have.value', 'TEST_CAM_01')
  })

  it('toggles B&W and FNAF filters', () => {
    cy.get('video').first().click({ force: true })

    // B&W Filter
    cy.contains('button', 'B&W').click()
    cy.get('video').first().should('have.class', 'grayscale')
    
    // FNAF Filter
    cy.contains('button', 'FNAF').click()
    // Check for overlay element specifically for this camera
    // structure is relative group -> video + overlay
    cy.get('.fnaf-overlay').should('exist')
  })

  it('navigates to standby on continue', () => {
    // Setup Camera 1 with filters
    cy.get('video').first().as('cam1').click({ force: true })
    cy.get('input[placeholder="ENTER DESIGNATOR"]').type('MONITOR_TEST')
    cy.contains('button', 'B&W').click()
    cy.contains('button', 'FNAF').click()

    // Continue
    cy.contains('button', 'Continue').click()

    // Should navigate to standby
    cy.url().should('include', '/standby')
  })
})
