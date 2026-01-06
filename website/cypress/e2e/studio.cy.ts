describe('LED Animation Studio', () => {
  beforeEach(() => {
    cy.visit('/studio')
  })

  describe('Page Load', () => {
    it('should display the page title', () => {
      cy.contains('Led Controller').should('be.visible')
      cy.contains('Animation Studio').should('be.visible')
    })

    it('should show the live preview section', () => {
      cy.contains('Live Preview').should('be.visible')
      cy.contains('STOPPED').should('be.visible')
    })

    it('should have at least one frame by default', () => {
      cy.contains('Frame 1').should('be.visible')
    })
  })

  describe('Frame Management', () => {
    it('should add a new frame when clicking Add Frame', () => {
      cy.contains('+ Add Frame').click()
      cy.contains('Frame 2').should('be.visible')
    })

    it('should remove a frame when clicking Remove', () => {
      // Add a second frame first
      cy.contains('+ Add Frame').click()
      cy.contains('Frame 2').should('be.visible')
      
      // Remove frame 2
      cy.get('button').contains('Remove').last().click()
      cy.contains('Frame 2').should('not.exist')
    })
  })

  describe('Preview Controls', () => {
    it('should start and stop the preview', () => {
      // Initially stopped
      cy.contains('STOPPED').should('be.visible')
      
      // Click play
      cy.contains('▶ Play').click()
      cy.contains('PLAYING').should('be.visible')
      
      // Click stop
      cy.contains('■ Stop').click()
      cy.contains('STOPPED').should('be.visible')
    })
  })

  describe('Brightness Control', () => {
    it('should have a brightness slider', () => {
      cy.contains('Global Brightness').should('be.visible')
      cy.get('input[type="range"]').first().should('exist')
    })
  })

  describe('Presets', () => {
    it('should load the Police Lights preset', () => {
      cy.get('select').select('Police Lights')
      // Should now have at least 2 frames from the preset
      cy.contains('Frame 2').should('be.visible')
    })

    it('should load the Rainbow Wave preset', () => {
      cy.get('select').select('Rainbow Wave')
      cy.contains('Frame 1').should('be.visible')
    })
  })

  describe('Export/Import', () => {
    it('should show JSON when clicking JSON button', () => {
      cy.contains('button', 'JSON').click()
      cy.get('textarea').should('be.visible')
      cy.get('textarea').should('contain.value', '"frames"')
    })

    it('should copy JSON to clipboard', () => {
      cy.contains('button', 'Copy').click()
      cy.contains('Copied!').should('be.visible')
    })

    it('should have a Download button', () => {
      cy.contains('button', 'Download').should('be.visible')
    })

    it('should have an Import button', () => {
      cy.contains('button', 'Import').should('be.visible')
    })
  })

  describe('Color Picker Modal', () => {
    it('should open color picker modal when clicking on a gradient stop', () => {
      // Click on a gradient stop (the white handle)
      cy.get('.absolute.-top-1').first().click()
      
      // Modal should appear
      cy.contains('Edit Color').should('be.visible')
      cy.contains('Pick Color').should('be.visible')
      cy.contains('Intensity (Alpha)').should('be.visible')
    })

    it('should close modal when clicking Done', () => {
      // Open modal
      cy.get('.absolute.-top-1').first().click()
      cy.contains('Edit Color').should('be.visible')
      
      // Close it
      cy.contains('Done').click()
      cy.contains('Edit Color').should('not.exist')
    })

    it('should delete a stop from the modal', () => {
      // Add a frame with multiple stops first
      cy.get('select').select('Rainbow Wave')
      
      // Open modal on a stop
      cy.get('.absolute.-top-1').first().click()
      cy.contains('Edit Color').should('be.visible')
      
      // Delete the stop
      cy.contains('Delete').click()
      cy.contains('Edit Color').should('not.exist')
    })
  })

  describe('Gradient Track Interaction', () => {
    it('should add a color stop when clicking on the track', () => {
      // Count initial stops
      cy.get('.absolute.-top-1').then($stops => {
        const initialCount = $stops.length
        
        // Click on the gradient track (the parent of the stops)
        cy.get('.h-8.relative.rounded.cursor-crosshair').first().click('center')
        
        // Should have one more stop
        cy.get('.absolute.-top-1').should('have.length.greaterThan', initialCount)
      })
    })
  })
})
