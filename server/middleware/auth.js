import dotenv from 'dotenv';
import jwt from 'jsonwebtoken';

dotenv.config();

const ADMIN_ID = process.env.ADMIN_ID;
const JWT_SECRET = process.env.JWT_SECRET || 'getolog_admin_secret_key_2026';

// Middleware to verify JWT token
export const verifyToken = (req, res, next) => {
  try {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

    if (!token) {
      return res.status(401).json({
        success: false,
        error: 'Authentication required',
        message: 'Access token not provided'
      });
    }

    jwt.verify(token, JWT_SECRET, (err, decoded) => {
      if (err) {
        return res.status(403).json({
          success: false,
          error: 'Invalid token',
          message: 'Token is expired or invalid'
        });
      }
      req.adminId = decoded.adminId;
      req.username = decoded.username;
      next();
    });
  } catch (error) {
    console.error('Auth middleware error:', error);
    return res.status(500).json({
      success: false,
      error: 'Authentication error',
      message: error.message
    });
  }
};

// Legacy middleware (kept for compatibility)
export const verifyManager = verifyToken;
export const devBypass = verifyToken;

export { JWT_SECRET };
