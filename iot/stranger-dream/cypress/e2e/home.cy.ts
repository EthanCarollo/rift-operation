/// <reference types="cypress" />

describe('Stranger Dream Home', () => {
    let mockSocket: any;

    beforeEach(() => {
        cy.visit('/', {
            onBeforeLoad(win) {
                // Create a mock WebSocket class
                class MockWebSocket {
                    url: string;
                    readyState: number;
                    onopen: Function | null = null;
                    onmessage: Function | null = null;
                    onclose: Function | null = null;
                    onerror: Function | null = null;
                    static OPEN = 1;

                    constructor(url: string) {
                        this.url = url;
                        this.readyState = MockWebSocket.OPEN;
                        mockSocket = this;
                        
                        // Simulate async connection
                        setTimeout(() => {
                            if (this.onopen) this.onopen();
                        }, 50);
                    }

                    close() {}
                    send() {}
                }
                
                // Stub the global WebSocket
                cy.stub(win, 'WebSocket').callsFake((url) => {
                    return new MockWebSocket(url);
                });
            }
        })
    })

    it('displays the main UI elements and connects', () => {
        cy.contains('h1', 'Stranger Dream').should('be.visible')
        // Check for specific tailwind classes to verify compilation
        cy.get('h1').should('have.class', 'text-6xl') 
        cy.get('img[alt="Banquise"]').should('be.visible')
        
        // Wait for connection simulation
        cy.wait(100)
        cy.get('div').contains('ONLINE').should('exist')
    })
    
    it('displays questions based on stranger_state', () => {
        // Wait for connection
        cy.wait(100)
        
        // Test Active State
        cy.then(() => {
            mockSocket.onmessage({ data: JSON.stringify({ stranger_state: 'active' }) })
        })
        cy.contains('h2', 'Is anyone listening?').should('be.visible')
        cy.contains('h1', 'Stranger Dream').should('not.exist') // Title hidden in active mode based on v-if/v-else
        
        // Test Step 2
        cy.then(() => {
            mockSocket.onmessage({ data: JSON.stringify({ stranger_state: 'step_2' }) })
        })
        cy.contains('h2', 'Can you hear the static?').should('be.visible')
        
        // Test Inactive (Return to base)
        cy.then(() => {
            mockSocket.onmessage({ data: JSON.stringify({ stranger_state: 'inactive' }) })
        })
        cy.contains('h1', 'Stranger Dream').should('be.visible')
        cy.contains('h2').should('not.exist')
    })
})
