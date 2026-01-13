// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "FluxTest",
    platforms: [
        .macOS(.v14)
    ],
    dependencies: [
        .package(url: "https://github.com/mzbac/flux.swift", branch: "main")
    ],
    targets: [
        .executableTarget(
            name: "FluxTest",
            dependencies: [
                .product(name: "FluxSwift", package: "flux.swift")
            ],
            path: "flux-dev-kontext-local"
        )
    ]
)
