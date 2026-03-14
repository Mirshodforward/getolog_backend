import express from 'express';
import { query } from '../config/database.js';

const router = express.Router();

// Get all transactions with pagination
router.get('/', async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const offset = (page - 1) * limit;
    const status = req.query.status; // optional filter
    const role = req.query.role; // optional filter

    // Build query
    let countQuery = 'SELECT COUNT(*) FROM transactions t';
    let selectQuery = `
      SELECT t.id, t.admin_id, t.user_id, t.username, t.amount,
             t.role, t.status, t.created_at,
             c.username as client_username
      FROM transactions t
      LEFT JOIN clients c ON t.admin_id = c.user_id
    `;

    const whereConditions = [];
    const params = [];
    let paramIndex = 1;

    if (status) {
      whereConditions.push(`t.status = $${paramIndex}`);
      params.push(status);
      paramIndex++;
    }

    if (role) {
      whereConditions.push(`t.role = $${paramIndex}`);
      params.push(role);
      paramIndex++;
    }

    if (whereConditions.length > 0) {
      const whereClause = ' WHERE ' + whereConditions.join(' AND ');
      countQuery += whereClause;
      selectQuery += whereClause;
    }

    selectQuery += ` ORDER BY t.created_at DESC LIMIT $${paramIndex} OFFSET $${paramIndex + 1}`;
    params.push(limit, offset);

    // Get total count
    const countResult = await query(
      countQuery,
      params.slice(0, -2) // exclude limit and offset
    );
    const totalCount = parseInt(countResult.rows[0].count);

    // Get transactions
    const transactionsResult = await query(selectQuery, params);

    res.json({
      success: true,
      data: {
        transactions: transactionsResult.rows.map((trans) => ({
          ...trans,
          amount: parseFloat(trans.amount) || 0,
        })),
        pagination: {
          total: totalCount,
          page,
          limit,
          totalPages: Math.ceil(totalCount / limit),
        },
      },
    });
  } catch (error) {
    console.error('Error fetching transactions:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch transactions',
      message: error.message,
    });
  }
});

// Get transaction by ID
router.get('/:transactionId', async (req, res) => {
  try {
    const transactionId = parseInt(req.params.transactionId);

    const transactionResult = await query(
      `SELECT t.*, c.username as client_username, c.phone_number as client_phone
       FROM transactions t
       LEFT JOIN clients c ON t.admin_id = c.user_id
       WHERE t.id = $1`,
      [transactionId]
    );

    if (transactionResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        error: 'Transaction not found',
      });
    }

    const transaction = transactionResult.rows[0];

    res.json({
      success: true,
      data: {
        transaction: {
          ...transaction,
          amount: parseFloat(transaction.amount) || 0,
        },
      },
    });
  } catch (error) {
    console.error('Error fetching transaction:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch transaction',
      message: error.message,
    });
  }
});

// Get pending transactions
router.get('/filter/pending', async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const offset = (page - 1) * limit;

    // Get total count
    const countResult = await query(
      "SELECT COUNT(*) FROM transactions WHERE status = 'pending'"
    );
    const totalCount = parseInt(countResult.rows[0].count);

    // Get pending transactions
    const transactionsResult = await query(
      `SELECT t.*, c.username as client_username
       FROM transactions t
       LEFT JOIN clients c ON t.admin_id = c.user_id
       WHERE t.status = 'pending'
       ORDER BY t.created_at DESC
       LIMIT $1 OFFSET $2`,
      [limit, offset]
    );

    res.json({
      success: true,
      data: {
        transactions: transactionsResult.rows.map((trans) => ({
          ...trans,
          amount: parseFloat(trans.amount) || 0,
        })),
        pagination: {
          total: totalCount,
          page,
          limit,
          totalPages: Math.ceil(totalCount / limit),
        },
      },
    });
  } catch (error) {
    console.error('Error fetching pending transactions:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch pending transactions',
      message: error.message,
    });
  }
});

// Update transaction status (approve/reject)
router.patch('/:transactionId/status', async (req, res) => {
  try {
    const transactionId = parseInt(req.params.transactionId);
    const { status } = req.body;

    if (!status || !['approved', 'rejected', 'pending'].includes(status)) {
      return res.status(400).json({
        success: false,
        error: 'Valid status is required (approved, rejected, or pending)',
      });
    }

    const result = await query(
      'UPDATE transactions SET status = $1 WHERE id = $2 RETURNING *',
      [status, transactionId]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        error: 'Transaction not found',
      });
    }

    res.json({
      success: true,
      data: {
        transaction: {
          ...result.rows[0],
          amount: parseFloat(result.rows[0].amount) || 0,
        },
      },
    });
  } catch (error) {
    console.error('Error updating transaction status:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to update transaction status',
      message: error.message,
    });
  }
});

// Get transactions by client (admin_id)
router.get('/by-client/:clientId', async (req, res) => {
  try {
    const clientId = parseInt(req.params.clientId);
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const offset = (page - 1) * limit;

    // Get total count
    const countResult = await query(
      'SELECT COUNT(*) FROM transactions WHERE admin_id = $1',
      [clientId]
    );
    const totalCount = parseInt(countResult.rows[0].count);

    // Get transactions
    const transactionsResult = await query(
      `SELECT id, user_id, username, amount, role, status, created_at
       FROM transactions
       WHERE admin_id = $1
       ORDER BY created_at DESC
       LIMIT $2 OFFSET $3`,
      [clientId, limit, offset]
    );

    res.json({
      success: true,
      data: {
        transactions: transactionsResult.rows.map((trans) => ({
          ...trans,
          amount: parseFloat(trans.amount) || 0,
        })),
        pagination: {
          total: totalCount,
          page,
          limit,
          totalPages: Math.ceil(totalCount / limit),
        },
      },
    });
  } catch (error) {
    console.error('Error fetching client transactions:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch transactions',
      message: error.message,
    });
  }
});

// Get transactions by user (user_id)
router.get('/by-user/:userId', async (req, res) => {
  try {
    const userId = parseInt(req.params.userId);

    const transactionsResult = await query(
      `SELECT id, admin_id, amount, role, status, created_at
       FROM transactions
       WHERE user_id = $1
       ORDER BY created_at DESC`,
      [userId]
    );

    res.json({
      success: true,
      data: {
        transactions: transactionsResult.rows.map((trans) => ({
          ...trans,
          amount: parseFloat(trans.amount) || 0,
        })),
      },
    });
  } catch (error) {
    console.error('Error fetching user transactions:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch transactions',
      message: error.message,
    });
  }
});

export default router;
