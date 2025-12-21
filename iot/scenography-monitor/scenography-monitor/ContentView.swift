//
//  ContentView.swift
//  scenography-monitor
//
//  Created by eth on 21/12/2025.
//

import SwiftUI

struct ContentView: View {
    // Bus Configuration
    let buses = [
        (id: 1, name: "Nightmare"),
        (id: 2, name: "Dream"),
        (id: 3, name: "Rift"),
        (id: 4, name: "SAS / OPERATOR")
    ]
    
    @State private var isInspectorOpen: Bool = false
    
    var body: some View {
        ZStack(alignment: .bottomTrailing) {
            
            HStack(spacing: 0) {
            
                // Main Content
                VStack(spacing: 0) {
                    // Toolbar / Header
                    HStack(alignment: .center) {
                        Image("RiftLogo")
                            .resizable()
                            .aspectRatio(contentMode: .fit)
                            .frame(height: 32)
                            .padding(.leading, 8)
                        
                        Text("RIFT OPERATION SOUND MONITOR")
                            .font(.system(size: 10, weight: .bold, design: .monospaced))
                            .opacity(0.5)
                        Spacer()
                        
                        // Stats
                        HStack(spacing: 8) {
                            Text("CPU: 12%")
                                .font(.system(size: 9, design: .monospaced))
                                .foregroundColor(.green)
                                .padding(.horizontal, 6)
                                .padding(.vertical, 2)
                                .background(Color.black)
                                .cornerRadius(2)
                            
                            Text("MEM: 480MB")
                                .font(.system(size: 9, design: .monospaced))
                                .foregroundColor(.orange)
                                .padding(.horizontal, 6)
                                .padding(.vertical, 2)
                                .background(Color.black)
                                .cornerRadius(2)
                        }
                        
                        Divider().frame(height: 20)
                        
                        // Inspector Toggle - MORE PROMINENT
                        Button(action: {
                            withAnimation {
                                isInspectorOpen.toggle()
                            }
                        }) {
                            HStack(spacing: 6) {
                                Image(systemName: "network")
                                Text("NETWORK CONFIG")
                                    .font(.system(size: 10, weight: .bold))
                            }
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(isInspectorOpen ? Color.blue.opacity(0.1) : Color.clear)
                            .foregroundColor(isInspectorOpen ? .blue : .primary)
                            .cornerRadius(4)
                            .overlay(
                                RoundedRectangle(cornerRadius: 4)
                                    .stroke(Color.gray.opacity(0.3), lineWidth: 1)
                            )
                        }
                        .buttonStyle(.plain)
                        .padding(.leading, 8)
                        
                    }
                    .padding(.horizontal)
                    .frame(height: 48) // Slightly taller for better touch target
                    .background(Color(nsColor: .controlBackgroundColor))
                    .border(Color(nsColor: .separatorColor), width: 1, edges: [.bottom])
                    
                    // Mixer Area
                    // Mixer Area
                    GeometryReader { geo in
                        ScrollView(.horizontal, showsIndicators: true) {
                            HStack(spacing: 0) {
                                ForEach(buses, id: \.id) { bus in
                                    AudioBusView(busName: bus.name, busId: bus.id)
                                        .frame(height: geo.size.height) // Match scroll view height
                                }
                            }
                            .padding(.horizontal)
                            .frame(minHeight: geo.size.height)
                        }
                    }
                    .background(Color(nsColor: .windowBackgroundColor))
                    
                    // Status Footer
                    HStack {
                        Text("READY")
                        Text("|")
                        Text("44.1kHz")
                        Spacer()
                    }
                    .font(.system(size: 9, design: .monospaced))
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal)
                    .frame(height: 24)
                    .background(Color(nsColor: .controlBackgroundColor))
                    .border(Color(nsColor: .separatorColor), width: 1, edges: [.top])
                }
                
                // Sidebar Area
                if isInspectorOpen {
                    WebSocketInspectorView(isVisible: $isInspectorOpen)
                        .frame(width: 250)
                        .transition(.move(edge: .trailing))
                        .zIndex(1)
                }
            }
            
            // DEV Badge (Overlay)
            Text("DEV")
                .font(.system(size: 12, weight: .bold))
                .foregroundColor(.white)
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(Color.red)
                .shadow(radius: 2)
                .padding(8)
        }
        .frame(minWidth: 900, minHeight: 500)
        .preferredColorScheme(.light) // Enforce Light Theme
    }
}

// Extension to allow single-edge borders easily
extension View {
    func border(_ color: Color, width: CGFloat, edges: [Edge]) -> some View {
        overlay(EdgeBorder(width: width, edges: edges).foregroundColor(color))
    }
}

struct EdgeBorder: Shape {
    var width: CGFloat
    var edges: [Edge]

    func path(in rect: CGRect) -> Path {
        var path = Path()
        for edge in edges {
            var x: CGFloat {
                switch edge {
                case .top, .bottom, .leading: return rect.minX
                case .trailing: return rect.maxX - width
                }
            }

            var y: CGFloat {
                switch edge {
                case .top, .leading, .trailing: return rect.minY
                case .bottom: return rect.maxY - width
                }
            }

            var w: CGFloat {
                switch edge {
                case .top, .bottom: return rect.width
                case .leading, .trailing: return width
                }
            }

            var h: CGFloat {
                switch edge {
                case .top, .bottom: return width
                case .leading, .trailing: return rect.height
                }
            }
            path.addPath(Path(CGRect(x: x, y: y, width: w, height: h)))
        }
        return path
    }
}
