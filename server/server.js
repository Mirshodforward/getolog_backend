import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import dotenv from 'dotenv';
import pool from './config/database.js';
import { devBypass } from './middleware/auth.js';

// Import routes
import authRoutes from './routes/auth.js';
import statsRoutes from './routes/stats.js';
import clientsRoutes from './routes/clients.js';
import botsRoutes from './routes/bots.js';
import usersRoutes from './routes/users.js';
import transactionsRoutes from './routes/transactions.js';
import exportRoutes from './routes/export.js';
import spendingsRoutes from './routes/spendings.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// ====== MIDDLEWARE ======

// Security headers
app.use(helmet());

// CORS configuration
const allowedOrigins = [
  'http://localhost:5173',
  'http://localhost:5174',
  'http://127.0.0.1:5173',
  'http://127.0.0.1:5174',
  'https://mirshodqahramonov.uz',
  'https://www.mirshodqahramonov.uz',
  ...(process.env.ALLOWED_ORIGINS ? process.env.ALLOWED_ORIGINS.split(',') : [])
];
app.use(
  cors({
    origin: function(origin, callback) {
      if (!origin || allowedOrigins.indexOf(origin) !== -1) {
        callback(null, true);
      } else {
        callback(new Error('Not allowed by CORS'));
      }
    },
    credentials: true,
  })
);

// Body parser
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.',
});

app.use('/api/', limiter);

// Request logging middleware
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});

// ====== ROUTES ======

// Health check
app.get('/', (req, res) => {
  res.json({
    success: true,
    message: 'Getolog Admin API Server',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
  });
});

// API health check
app.get('/api/health', async (req, res) => {
  try {
    // Test database connection
    await pool.query('SELECT 1');

    res.json({
      success: true,
      message: 'API is healthy',
      database: 'connected',
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'API is unhealthy',
      database: 'disconnected',
      error: error.message,
    });
  }
});

// Auth routes (no JWT required)
app.use('/api/auth', authRoutes);

// Apply auth middleware to all API routes (JWT verification)
app.use('/api', devBypass);

// API Routes
app.use('/api/stats', statsRoutes);
app.use('/api/clients', clientsRoutes);
app.use('/api/bots', botsRoutes);
app.use('/api/users', usersRoutes);
app.use('/api/transactions', transactionsRoutes);
app.use('/api/export', exportRoutes);
app.use('/api/spendings', spendingsRoutes);

// ====== ERROR HANDLING ======

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    success: false,
    error: 'Route not found',
    path: req.path,
  });
});

// Global error handler
app.use((err, req, res, next) => {
  console.error('Global error handler:', err);

  res.status(err.status || 500).json({
    success: false,
    error: err.message || 'Internal server error',
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack }),
  });
});

// ====== START SERVER ======

app.listen(PORT, () => {
  console.log('');
  console.log('='.repeat(60));
  console.log(`🚀 Getolog Admin API Server`);
  console.log(`🌐 Server running on: http://localhost:${PORT}`);
  console.log(`🔧 Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`📊 Database: ${process.env.DB_NAME}@${process.env.DB_HOST}:${process.env.DB_PORT}`);
  console.log('='.repeat(60));
  console.log('');
  console.log('Available endpoints:');
  console.log('  GET  /                          - API info');
  console.log('  GET  /api/health                - Health check');
  console.log('');
  console.log('  GET  /api/stats/global          - Global statistics');
  console.log('  GET  /api/stats/activity        - Recent activity');
  console.log('');
  console.log('  GET  /api/clients               - List all clients');
  console.log('  GET  /api/clients/search        - Search clients');
  console.log('  GET  /api/clients/:id           - Get client details');
  console.log('  PATCH /api/clients/:id/balance  - Update client balance');
  console.log('');
  console.log('  GET  /api/bots                  - List all bots');
  console.log('  GET  /api/bots/:id              - Get bot details');
  console.log('');
  console.log('  GET  /api/users                 - List all users');
  console.log('  GET  /api/users/:id             - Get user details');
  console.log('');
  console.log('  GET  /api/transactions          - List all transactions');
  console.log('  GET  /api/transactions/filter/pending - Pending transactions');
  console.log('');
  console.log('  GET  /api/spendings             - List all spendings');
  console.log('  GET  /api/spendings/stats       - Spending statistics');
  console.log('  GET  /api/spendings/user/:id    - User spendings');
  console.log('  GET  /api/spendings/admin/:id   - Admin earnings');
  console.log('');
  console.log('  GET  /api/export/all            - Export all data to Excel');
  console.log('  GET  /api/export/clients        - Export clients to Excel');
  console.log('  GET  /api/export/transactions   - Export transactions to Excel');
  console.log('='.repeat(60));
  console.log('');
});

// Handle graceful shutdown
process.on('SIGTERM', async () => {
  console.log('SIGTERM received, closing server...');
  await pool.end();
  process.exit(0);
});

process.on('SIGINT', async () => {
  console.log('SIGINT received, closing server...');
  await pool.end();
  process.exit(0);
});

export default app;
