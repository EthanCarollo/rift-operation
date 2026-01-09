/// <reference types="cypress" />

describe('Config Page', () => {
  beforeEach(() => {
    cy.visit('/config')
  })

  it('should display the config page header', () => {
    cy.contains('Battle Camera Config').should('be.visible')
  })

  it('should show connection status', () => {
    cy.get('[class*="flex items-center gap-2"]').should('exist')
  })

  it('should display battle status panel', () => {
    cy.contains('Battle Status').should('be.visible')
    cy.contains('State').should('be.visible')
    cy.contains('Current Attack').should('be.visible')
    cy.contains('Running').should('be.visible')
  })

  it('should display nightmare camera section', () => {
    cy.contains('Nightmare Camera').should('be.visible')
    cy.get('select').first().should('exist')
  })

  it('should display dream camera section', () => {
    cy.contains('Dream Camera').should('be.visible')
  })

  it('should have camera preview containers', () => {
    cy.get('[class*="aspect-video"]').should('have.length.at.least', 2)
  })

  it('should allow camera selection change', () => {
    cy.get('select').first().select(0)
    // Should not throw an error
  })

  it('should show output preview sections', () => {
    cy.contains('Nightmare Output').should('be.visible')
    cy.contains('Dream Output').should('be.visible')
  })

  it('should have navigation back to battle', () => {
    cy.contains('Back to Battle').should('exist')
  })
})

describe('Battle Page', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  it('should display role selection screen', () => {
    cy.contains('BATAILLE FINALE').should('be.visible')
  })

  it('should have dream role button', () => {
    cy.contains('button', 'DREAM').should('be.visible')
  })

  it('should have nightmare role button', () => {
    cy.contains('button', 'NIGHTMARE').should('be.visible')
  })

  it('should select dream role when clicked', () => {
    cy.contains('button', 'DREAM').click()
    // Should transition to battle view (role selection disappears)
    cy.contains('BATAILLE FINALE').should('not.exist')
  })

  it('should select nightmare role when clicked', () => {
    cy.visit('/')
    cy.contains('button', 'NIGHTMARE').click()
    cy.contains('BATAILLE FINALE').should('not.exist')
  })
})
