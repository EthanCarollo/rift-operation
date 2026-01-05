/// <reference types="cypress" />

describe('Stranger Dream Home', () => {
    it('displays the main UI elements', () => {
        cy.visit('/')
        cy.contains('h1', 'Stranger Dream').should('be.visible')
        // Check for specific tailwind classes to verify compilation
        cy.get('h1').should('have.class', 'text-6xl') // Verify tailwind applied
        cy.get('img[alt="Banquise"]').should('be.visible')
    })
    
    it('shows connection status', () => {
        cy.visit('/')
        // Initial state should generally be "CONNECTING..." or "ONLINE"
        // We just verify the element exists
        cy.get('div').contains(/CONNECTING\.\.\.|ONLINE/).should('exist')
    })
})
