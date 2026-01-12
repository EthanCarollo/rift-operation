/// <reference types="cypress" />

/**
 * E2E tests for Stranger Dream application
 * Testing: Dev panel, state transitions, components
 */

describe('Stranger Dream - Component Tests', () => {
    let mockSocket: any;

    // Helper to create mock WebSocket
    const setupMockWebSocket = (win: Cypress.AUTWindow) => {
        class MockWebSocket {
            url: string;
            readyState: number;
            onopen: Function | null = null;
            onmessage: Function | null = null;
            onclose: Function | null = null;
            onerror: Function | null = null;
            static OPEN = 1;
            static CLOSED = 3;

            constructor(url: string) {
                this.url = url;
                this.readyState = MockWebSocket.OPEN;
                mockSocket = this;
                
                setTimeout(() => {
                    if (this.onopen) this.onopen();
                }, 50);
            }

            close() {
                this.readyState = MockWebSocket.CLOSED;
                if (this.onclose) this.onclose();
            }
            send(data: string) {
                console.log('MockWebSocket send:', data);
            }
        }
        
        cy.stub(win, 'WebSocket').callsFake((url) => {
            return new MockWebSocket(url);
        });
    };

    beforeEach(() => {
        cy.visit('/', {
            onBeforeLoad(win) {
                setupMockWebSocket(win);
            }
        });
    });

    describe('Dev Panel', () => {
        it('should display the dev panel in dev mode', () => {
            cy.get('[data-testid="dev-panel"]').should('exist');
            cy.get('[data-testid="dev-panel"]').should('be.visible');
        });

        it('should display the status indicator', () => {
            cy.get('[data-testid="dev-status-indicator"]').should('exist');
            cy.get('[data-testid="dev-status-indicator"]').should('be.visible');
        });

        it('should have state buttons', () => {
            cy.get('[data-testid="dev-panel"]').within(() => {
                cy.contains('button', 'INACTIVE').should('exist');
                cy.contains('button', 'ACTIVE').should('exist');
                cy.contains('button', 'S2').should('exist');
                cy.contains('button', 'S3').should('exist');
                cy.contains('button', 'S4').should('exist');
            });
        });

        it('should have URL input and reconnect button', () => {
            cy.get('[data-testid="dev-panel"]').within(() => {
                cy.get('input[type="text"]').should('exist');
                cy.contains('button', 'UPDATE CONNECTION').should('exist');
            });
        });

        it('should switch to active state when clicking ACTIVE button', () => {
            cy.wait(500);
            cy.get('[data-testid="dev-panel"]').within(() => {
                cy.contains('button', /^ACTIVE$/).click();
            });
            // Puzzle view should be visible - check for puzzle content
            cy.contains('Étape 1').should('be.visible');
        });

        it('should switch to step_2 state when clicking S2 button', () => {
            cy.wait(100);
            cy.get('[data-testid="dev-panel"]').within(() => {
                cy.contains('button', 'S2').click();
            });
            cy.contains('QUESTION 2').should('be.visible');
        });

        it('should switch to step_3 state when clicking S3 button', () => {
            cy.wait(100);
            cy.get('[data-testid="dev-panel"]').within(() => {
                cy.contains('button', 'S3').click();
            });
            cy.contains('Demandez gentiment').should('be.visible');
        });

        it('should switch to step_4 state when clicking S4 button', () => {
            cy.wait(100);
            cy.get('[data-testid="dev-panel"]').within(() => {
                cy.contains('button', 'S4').click();
            });
            cy.contains('Ramenez Dark Cosmo').should('be.visible');
        });

        it('should return to inactive state when clicking INACTIVE button', () => {
            cy.wait(100);
            // First go to active
            cy.get('[data-testid="dev-panel"]').within(() => {
                cy.contains('button', /^ACTIVE$/).click();
            });
            cy.contains('Étape 1').should('be.visible');
            
            // Then go back to inactive
            cy.get('[data-testid="dev-panel"]').within(() => {
                cy.contains('button', 'INACTIVE').click();
            });
            // Content should be gone
            cy.contains('Étape 1').should('not.exist');
        });
    });

    describe('Candy Container', () => {
        it('should display the candy container when active', () => {
            cy.wait(100);
            cy.get('[data-testid="dev-panel"]').within(() => {
                cy.contains('button', /^ACTIVE$/).click();
            });
            // Candy container should exist (look for the candy background image)
            cy.get('img[src="/images/stranger/question-container-candy.png"]').should('be.visible');
        });
    });

    describe('Step Pagination', () => {
        it('should display step numbers when active', () => {
            cy.wait(100);
            cy.get('[data-testid="dev-panel"]').within(() => {
                cy.contains('button', /^ACTIVE$/).click();
            });
            // Check for step numbers in pagination
            cy.contains('span', '1').should('exist');
            cy.contains('span', '2').should('exist');
            cy.contains('span', '3').should('exist');
            cy.contains('span', '4').should('exist');
        });
    });

    describe('Puzzle View', () => {
        it('should display puzzle title for active state', () => {
            cy.wait(100);
            cy.get('[data-testid="dev-panel"]').within(() => {
                cy.contains('button', /^ACTIVE$/).click();
            });
            cy.contains('Étape 1').should('be.visible');
        });

        it('should display puzzle items with images', () => {
            cy.wait(100);
            cy.get('[data-testid="dev-panel"]').within(() => {
                cy.contains('button', /^ACTIVE$/).click();
            });
            cy.get('img[src*="hat"]').should('have.length', 3);
        });

        it('should display puzzle letters', () => {
            cy.wait(100);
            cy.get('[data-testid="dev-panel"]').within(() => {
                cy.contains('button', /^ACTIVE$/).click();
            });
            cy.contains('B').should('exist');
            cy.contains('i').should('exist');
            cy.contains('P').should('exist');
        });
    });

    describe('Text View', () => {
        it('should display text view for step_2', () => {
            cy.wait(100);
            cy.get('[data-testid="dev-panel"]').within(() => {
                cy.contains('button', 'S2').click();
            });
            cy.contains('QUESTION 2').should('be.visible');
        });

        it('should display text content for step_3', () => {
            cy.wait(100);
            cy.get('[data-testid="dev-panel"]').within(() => {
                cy.contains('button', 'S3').click();
            });
            cy.contains('Cosmo').should('be.visible');
        });
    });

    describe('State Transitions via WebSocket', () => {
        beforeEach(() => {
            cy.wait(100);
        });

        it('should show inactive state by default (no content)', () => {
            cy.contains('Étape 1').should('not.exist');
            cy.contains('QUESTION 2').should('not.exist');
        });

        it('should display puzzle question when receiving active state', () => {
            cy.then(() => {
                mockSocket.onmessage({ data: JSON.stringify({ stranger_state: 'active' }) });
            });
            cy.contains('Étape 1').should('be.visible');
        });

        it('should display text question when receiving step_2 state', () => {
            cy.then(() => {
                mockSocket.onmessage({ data: JSON.stringify({ stranger_state: 'step_2' }) });
            });
            cy.contains('QUESTION 2').should('be.visible');
        });

        it('should transition through all states correctly', () => {
            // inactive -> active
            cy.then(() => {
                mockSocket.onmessage({ data: JSON.stringify({ stranger_state: 'active' }) });
            });
            cy.contains('Étape 1').should('be.visible');
            
            // active -> step_2
            cy.then(() => {
                mockSocket.onmessage({ data: JSON.stringify({ stranger_state: 'step_2' }) });
            });
            cy.contains('QUESTION 2').should('be.visible');
            
            // step_2 -> step_3
            cy.then(() => {
                mockSocket.onmessage({ data: JSON.stringify({ stranger_state: 'step_3' }) });
            });
            cy.contains('Demandez gentiment').should('be.visible');
            
            // step_3 -> step_4
            cy.then(() => {
                mockSocket.onmessage({ data: JSON.stringify({ stranger_state: 'step_4' }) });
            });
            cy.contains('Ramenez Dark Cosmo').should('be.visible');
            
            // step_4 -> inactive
            cy.then(() => {
                mockSocket.onmessage({ data: JSON.stringify({ stranger_state: 'inactive' }) });
            });
            cy.contains('Ramenez Dark Cosmo').should('not.exist');
        });
    });

    describe('Visual Layout', () => {
        it('should have dev panel with fixed position', () => {
            cy.get('[data-testid="dev-panel"]').should('have.css', 'position', 'fixed');
        });

        it('should have high z-index for dev panel', () => {
            cy.get('[data-testid="dev-panel"]').should('have.css', 'z-index', '50');
        });
    });
});
