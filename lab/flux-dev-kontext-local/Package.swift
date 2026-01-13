// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "FluxTest",
    platforms: [
        .macOS(.v14)
    ],
    dependencies: [
        .package(url: "https://github.com/mzbac/flux.swift.git", from: "0.1.3"),
    .package(url: "https://github.com/ml-explore/mlx-swift", .upToNextMinor(from: "0.25.4")),
    .package(url: "https://github.com/huggingface/swift-transformers",.upToNextMinor(from: "0.1.21")),
    .package(url: "https://github.com/apple/swift-log.git", from: "1.5.3"),
    ],
    targets: [
        .executableTarget(
            name: "FluxTest",
            dependencies: [
                .product(name: "MLX", package: "mlx-swift"),
                .product(name: "MLXFast", package: "mlx-swift"),
                .product(name: "MLXNN", package: "mlx-swift"),
                .product(name: "MLXOptimizers", package: "mlx-swift"),
                .product(name: "MLXRandom", package: "mlx-swift"),
                .product(name: "Transformers", package: "swift-transformers"),
                .product(name: "Logging", package: "swift-log"),
                .product(name: "FluxSwift", package: "flux.swift")
            ],
            path: "flux-dev-kontext-local"
        )
    ]
)
