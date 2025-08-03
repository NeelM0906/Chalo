// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "LocalWanderBackend",
    platforms: [
        .macOS(.v13)
    ],
    dependencies: [
        .package(url: "https://github.com/vapor/vapor.git", from: "4.0.0"),
        .package(url: "https://github.com/vapor/fluent.git", from: "4.0.0"),
        .package(url: "https://github.com/vapor/fluent-sqlite-driver.git", from: "4.0.0"),
    ],
    targets: [
        .executableTarget(
            name: "LocalWanderBackend",
            dependencies: [
                .product(name: "Vapor", package: "vapor"),
                .product(name: "Fluent", package: "fluent"),
                .product(name: "FluentSQLiteDriver", package: "fluent-sqlite-driver"),
            ],
            path: "Sources"
        ),
        .testTarget(
            name: "LocalWanderBackendTests",
            dependencies: [
                .target(name: "LocalWanderBackend"),
                .product(name: "XCTVapor", package: "vapor"),
            ],
            path: "Tests"
        ),
    ]
) 