import express from 'express';
import jwt from 'jsonwebtoken';
import { JWT_SECRET } from '../middleware/auth.js';

const router = express.Router();

// Admin credentials
const ADMIN_USERNAME = process.env.ADMIN_USERNAME || 'admin';

// POST /api/auth/login
router.post('/login', (req, res) => {
  try {
    const ADMIN_USERNAME = process.env.ADMIN_USERNAME || 'admin';

    // Generate JWT token (expires in 24 hours)
    const token = jwt.sign(
      { adminId: ADMIN_USERNAME, username: ADMIN_USERNAME },
      JWT_SECRET,
      { expiresIn: '24h' }
    );

    res.json({
      success: true,
      data: {
        token,
        username: ADMIN_USERNAME,
        expiresIn: '24h',
      },
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({
      success: false,
      error: 'Login failed',
      message: error.message,
    });
  }
});

// GET /api/auth/verify - verify token is still valid
router.get('/verify', (req, res) => {
  try {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) {
      return res.status(401).json({ success: false, error: 'No token' });
    }

    jwt.verify(token, JWT_SECRET, (err, decoded) => {
      if (err) {
        return res.status(403).json({ success: false, error: 'Invalid token' });
      }
      res.json({
        success: true,
        data: { username: decoded.username },
      });
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

export default router;
