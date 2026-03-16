import express from 'express';
import { query } from '../config/database.js';

const router = express.Router();

// Get all clients with pagination
router.get('/', async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const offset = (page - 1) * limit;

    // Get total count
    const countResult = await query('SELECT COUNT(*) FROM clients');
    const totalCount = parseInt(countResult.rows[0].count);

    // Get clients with pagination
    const clientsResult = await query(
      `SELECT id, user_id, username, phone_number, balance, plan_type, language, created_at
       FROM clients
       ORDER BY created_at DESC
       LIMIT $1 OFFSET $2`,
      [limit, offset]
    );

    // Get bot count for each client
    const clientsWithBots = await Promise.all(
      clientsResult.rows.map(async (client) => {
        const botsResult = await query(
          'SELECT COUNT(*) FROM client_bots WHERE user_id = $1',
          [client.user_id]
        );
        const usersResult = await query(
          'SELECT COUNT(*) FROM users WHERE admin_id = $1',
          [client.user_id]
        );

        return {
          ...client,
          balance: parseFloat(client.balance) || 0,
          bots_count: parseInt(botsResult.rows[0].count),
          users_count: parseInt(usersResult.rows[0].count),
        };
      })
    );

    res.json({
      success: true,
      data: {
        clients: clientsWithBots,
        pagination: {
          total: totalCount,
          page,
          limit,
          totalPages: Math.ceil(totalCount / limit),
        },
      },
    });
  } catch (error) {
    console.error('Error fetching clients:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch clients',
      message: error.message,
    });
  }
});

// Search client by ID or username
router.get('/search', async (req, res) => {
  try {
    const { query: searchQuery } = req.query;

    if (!searchQuery) {
      return res.status(400).json({
        success: false,
        error: 'Search query required',
      });
    }

    let clientResult;
    const searchTrimmed = searchQuery.trim();

    // Check if search is numeric (user_id)
    if (!isNaN(searchTrimmed) && searchTrimmed.length < 15) {
      clientResult = await query(
        'SELECT * FROM clients WHERE user_id = $1 OR phone_number LIKE $2',
        [parseInt(searchTrimmed), `%${searchTrimmed}%`]
      );
    } else if (searchTrimmed.startsWith('+') || searchTrimmed.replace(/\D/g, '').length >= 9) {
      // Search by phone number
      const phoneDigits = searchTrimmed.replace(/\D/g, '');
      clientResult = await query(
        'SELECT * FROM clients WHERE phone_number LIKE $1',
        [`%${phoneDigits}%`]
      );
    } else {
      // Search by username
      const username = searchTrimmed.replace('@', '');
      clientResult = await query(
        'SELECT * FROM clients WHERE username ILIKE $1',
        [`%${username}%`]
      );
    }

    // Get bot/user counts for search results
    const clientsWithBots = await Promise.all(
      clientResult.rows.map(async (client) => {
        const botsResult = await query(
          'SELECT COUNT(*) FROM client_bots WHERE user_id = $1',
          [client.user_id]
        );
        const usersResult = await query(
          'SELECT COUNT(*) FROM users WHERE admin_id = $1',
          [client.user_id]
        );
        return {
          ...client,
          balance: parseFloat(client.balance) || 0,
          bots_count: parseInt(botsResult.rows[0].count),
          users_count: parseInt(usersResult.rows[0].count),
        };
      })
    );

    res.json({
      success: true,
      data: {
        clients: clientsWithBots,
      },
    });
  } catch (error) {
    console.error('Error searching client:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to search client',
      message: error.message,
    });
  }
});

// Get client details by user_id
router.get('/:userId', async (req, res) => {
  try {
    const userId = parseInt(req.params.userId);

    // Get client info
    const clientResult = await query(
      'SELECT * FROM clients WHERE user_id = $1',
      [userId]
    );

    if (clientResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        error: 'Client not found',
      });
    }

    const client = clientResult.rows[0];

    // Get client's bots
    const botsResult = await query(
      `SELECT id, bot_username, status, channel_id, created_at
       FROM client_bots
       WHERE user_id = $1
       ORDER BY created_at DESC`,
      [userId]
    );

    // Get client's users count
    const usersCountResult = await query(
      'SELECT COUNT(*) FROM users WHERE admin_id = $1',
      [userId]
    );

    // Get client's total revenue
    const revenueResult = await query(
      `SELECT COALESCE(SUM(amount), 0) as total
       FROM transactions
       WHERE admin_id = $1 AND status = 'approved'`,
      [userId]
    );

    res.json({
      success: true,
      data: {
        client: {
          ...client,
          balance: parseFloat(client.balance) || 0,
        },
        bots: botsResult.rows,
        users_count: parseInt(usersCountResult.rows[0].count),
        total_revenue: parseFloat(revenueResult.rows[0].total) || 0,
      },
    });
  } catch (error) {
    console.error('Error fetching client details:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch client details',
      message: error.message,
    });
  }
});

// Update client balance (add or subtract)
router.patch('/:userId/balance', async (req, res) => {
  try {
    const userId = parseInt(req.params.userId);
    const { amount, action } = req.body; // action: 'add' or 'subtract'

    if (!amount || !action) {
      return res.status(400).json({
        success: false,
        error: 'Amount and action are required',
      });
    }

    const parsedAmount = parseFloat(amount);

    if (isNaN(parsedAmount) || parsedAmount <= 0) {
      return res.status(400).json({
        success: false,
        error: 'Invalid amount',
      });
    }

    // Update balance
    let updateQuery;
    if (action === 'add') {
      updateQuery = `
        UPDATE clients
        SET balance = COALESCE(balance, 0) + $1
        WHERE user_id = $2
        RETURNING balance
      `;
    } else if (action === 'subtract') {
      updateQuery = `
        UPDATE clients
        SET balance = COALESCE(balance, 0) - $1
        WHERE user_id = $2
        RETURNING balance
      `;
    } else {
      return res.status(400).json({
        success: false,
        error: 'Invalid action. Use "add" or "subtract"',
      });
    }

    const result = await query(updateQuery, [parsedAmount, userId]);

    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        error: 'Client not found',
      });
    }

    res.json({
      success: true,
      data: {
        user_id: userId,
        new_balance: parseFloat(result.rows[0].balance),
        action,
        amount: parsedAmount,
      },
    });
  } catch (error) {
    console.error('Error updating balance:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to update balance',
      message: error.message,
    });
  }
});

// Get client's bots
router.get('/:userId/bots', async (req, res) => {
  try {
    const userId = parseInt(req.params.userId);

    const botsResult = await query(
      `SELECT id, bot_username, bot_token, channel_id, status,
              oy_narx, yil_narx, cheksiz_narx, card_number, created_at
       FROM client_bots
       WHERE user_id = $1
       ORDER BY created_at DESC`,
      [userId]
    );

    res.json({
      success: true,
      data: {
        bots: botsResult.rows.map((bot) => ({
          ...bot,
          oy_narx: parseFloat(bot.oy_narx) || 0,
          yil_narx: parseFloat(bot.yil_narx) || 0,
          cheksiz_narx: parseFloat(bot.cheksiz_narx) || 0,
        })),
      },
    });
  } catch (error) {
    console.error('Error fetching client bots:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch client bots',
      message: error.message,
    });
  }
});

// Get client's users
router.get('/:userId/users', async (req, res) => {
  try {
    const userId = parseInt(req.params.userId);
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const offset = (page - 1) * limit;

    // Get total count
    const countResult = await query(
      'SELECT COUNT(*) FROM users WHERE admin_id = $1',
      [userId]
    );
    const totalCount = parseInt(countResult.rows[0].count);

    // Get users
    const usersResult = await query(
      `SELECT id, user_id, username, name, duration, balance, status,
              invite_link, created_at
       FROM users
       WHERE admin_id = $1
       ORDER BY created_at DESC
       LIMIT $2 OFFSET $3`,
      [userId, limit, offset]
    );

    res.json({
      success: true,
      data: {
        users: usersResult.rows.map((user) => ({
          ...user,
          balance: parseFloat(user.balance) || 0,
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
    console.error('Error fetching client users:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch client users',
      message: error.message,
    });
  }
});

export default router;
