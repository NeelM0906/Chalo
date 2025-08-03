import Vapor
import Fluent
import FluentSQLiteDriver

var env = try Environment.detect()
try LoggingSystem.bootstrap(from: &env)
let app = Application(env)
defer { app.shutdown() }

// Configure database
app.databases.use(.sqlite(.file("db.sqlite")), as: .sqlite)

// Configure CORS
let corsConfiguration = CORSMiddleware.Configuration(
    allowedOrigin: .all,
    allowedMethods: [.GET, .POST, .PUT, .OPTIONS, .DELETE, .PATCH],
    allowedHeaders: [.accept, .authorization, .contentType, .origin, .xRequestedWith, .userAgent, .accessControlAllowOrigin]
)
app.middleware.use(CORSMiddleware(configuration: corsConfiguration))

// Register routes
try routes(app)

try app.run() 