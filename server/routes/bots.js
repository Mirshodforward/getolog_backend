import express from 'express';
import { exec } from 'child_process';
import { query } from '../config/database.js';

const router = express.Router();

// Get deleted bots with pagination
router.get('/deleted', async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const offset = (page - 1) * limit;

    // Get total count
    const countResult = await query('SELECT COUNT(*) FROM deleted_bots');
    const totalCount = parseInt(countResult.rows[0].count);

    // Get deleted bots with owner info
    const botsResult = await query(
      `SELECT db.*, c.username as owner_username
       FROM deleted_bots db
       LEFT JOIN clients c ON db.user_id = c.user_id
       ORDER BY db.deleted_at DESC
       LIMIT $1 OFFSET $2`,
      [limit, offset]
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
        pagination: {
          total: totalCount,
          page,
          limit,
          totalPages: Math.ceil(totalCount / limit),
        },
      },
    });
  } catch (error) {
    console.error('Error fetching deleted bots:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch deleted bots',
      message: error.message,
    });
  }
});

// Get all bots with pagination
router.get('/', async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const offset = (page - 1) * limit;

    // Get total count
    const countResult = await query('SELECT COUNT(*) FROM client_bots');
    const totalCount = parseInt(countResult.rows[0].count);

    // Get bots with owner info (including new fields)
    const botsResult = await query(
      `SELECT cb.id, cb.user_id, cb.bot_name, cb.bot_token, cb.bot_username,
              cb.channel_id, cb.manager_invite_link,
              cb.status, cb.process_id, cb.should_stop, cb.oy_narx, cb.yil_narx, cb.cheksiz_narx,
              cb.card_number, cb.created_at,
              c.username as owner_username
       FROM client_bots cb
       LEFT JOIN clients c ON cb.user_id = c.user_id
       ORDER BY cb.created_at DESC
       LIMIT $1 OFFSET $2`,
      [limit, offset]
    );

    // Get users count for each bot
    const botsWithUsers = await Promise.all(
      botsResult.rows.map(async (bot) => {
        const usersResult = await query(
          'SELECT COUNT(*) FROM users WHERE admin_id = $1',
          [bot.user_id]
        );

        return {
          ...bot,
          oy_narx: parseFloat(bot.oy_narx) || 0,
          yil_narx: parseFloat(bot.yil_narx) || 0,
          cheksiz_narx: parseFloat(bot.cheksiz_narx) || 0,
          users_count: parseInt(usersResult.rows[0].count),
        };
      })
    );

    res.json({
      success: true,
      data: {
        bots: botsWithUsers,
        pagination: {
          total: totalCount,
          page,
          limit,
          totalPages: Math.ceil(totalCount / limit),
        },
      },
    });
  } catch (error) {
    console.error('Error fetching bots:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch bots',
      message: error.message,
    });
  }
});

// Get bot details by ID
router.get('/:botId', async (req, res) => {
  try {
    const botId = parseInt(req.params.botId);

    // Get bot info with owner details
    const botResult = await query(
      `SELECT cb.*, c.username as owner_username, c.phone_number as owner_phone
       FROM client_bots cb
       LEFT JOIN clients c ON cb.user_id = c.user_id
       WHERE cb.id = $1`,
      [botId]
    );

    if (botResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        error: 'Bot not found',
      });
    }

    const bot = botResult.rows[0];

    // Get bot's users count
    const usersCountResult = await query(
      'SELECT COUNT(*) FROM users WHERE admin_id = $1',
      [bot.user_id]
    );

    // Get bot's active users count
    const activeUsersResult = await query(
      "SELECT COUNT(*) FROM users WHERE admin_id = $1 AND status = 'active'",
      [bot.user_id]
    );

    // Get bot's total revenue
    const revenueResult = await query(
      `SELECT COALESCE(SUM(amount), 0) as total
       FROM transactions
       WHERE admin_id = $1 AND status = 'approved'`,
      [bot.user_id]
    );

    res.json({
      success: true,
      data: {
        bot: {
          ...bot,
          oy_narx: parseFloat(bot.oy_narx) || 0,
          yil_narx: parseFloat(bot.yil_narx) || 0,
          cheksiz_narx: parseFloat(bot.cheksiz_narx) || 0,
        },
        stats: {
          total_users: parseInt(usersCountResult.rows[0].count),
          active_users: parseInt(activeUsersResult.rows[0].count),
          total_revenue: parseFloat(revenueResult.rows[0].total) || 0,
        },
      },
    });
  } catch (error) {
    console.error('Error fetching bot details:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch bot details',
      message: error.message,
    });
  }
});

// Update bot status
router.patch('/:botId/status', async (req, res) => {
  try {
    const botId = parseInt(req.params.botId);
    const { status } = req.body;

    if (!status || !['active', 'inactive'].includes(status)) {
      return res.status(400).json({
        success: false,
        error: 'Valid status is required (active or inactive)',
      });
    }

    const result = await query(
      'UPDATE client_bots SET status = $1 WHERE id = $2 RETURNING *',
      [status, botId]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        error: 'Bot not found',
      });
    }

    res.json({
      success: true,
      data: {
        bot: result.rows[0],
      },
    });
  } catch (error) {
    console.error('Error updating bot status:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to update bot status',
      message: error.message,
    });
  }
});

// Get bot's users
router.get('/:botId/users', async (req, res) => {
  try {
    const botId = parseInt(req.params.botId);

    // First get the bot's owner user_id
    const botResult = await query(
      'SELECT user_id FROM client_bots WHERE id = $1',
      [botId]
    );

    if (botResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        error: 'Bot not found',
      });
    }

    const ownerId = botResult.rows[0].user_id;

    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const offset = (page - 1) * limit;

    // Get total count
    const countResult = await query(
      'SELECT COUNT(*) FROM users WHERE admin_id = $1',
      [ownerId]
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
      [ownerId, limit, offset]
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
    console.error('Error fetching bot users:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch bot users',
      message: error.message,
    });
  }
});

// Stop bot - faqat should_stop flagini o'zgartiradi
// Bot daemon har 5 sekundda tekshiradi va o'zi to'xtatadi
router.post('/:botId/stop', async (req, res) => {
  try {
    const botId = parseInt(req.params.botId);

    // Get bot info
    const botResult = await query(
      'SELECT * FROM client_bots WHERE id = $1',
      [botId]
    );

    if (botResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        error: 'Bot not found',
      });
    }

    const bot = botResult.rows[0];

    // Check if bot is already stopped
    if (bot.should_stop === true && bot.status === 'stopped') {
      return res.status(400).json({
        success: false,
        error: 'Bot is already stopped',
      });
    }

    // Faqat should_stop flagini true qilamiz
    // Bot o'zi har 5 sekundda tekshiradi va to'xtaydi
    const result = await query(
      `UPDATE client_bots
       SET should_stop = true
       WHERE id = $1
       RETURNING *`,
      [botId]
    );

    console.log(`🛑 Stop signal sent to bot ${bot.bot_name} (ID: ${botId})`);

    res.json({
      success: true,
      message: "To'xtatish signali yuborildi. Bot 5-10 sekund ichida to'xtaydi.",
      data: { bot: result.rows[0] },
    });
  } catch (error) {
    console.error('Error stopping bot:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to stop bot',
      message: error.message,
    });
  }
});

// Start bot - faqat should_stop flagini o'zgartiradi
// Bot daemon har 5 sekundda tekshiradi va o'zi ishga tushiradi
router.post('/:botId/start', async (req, res) => {
  try {
    const botId = parseInt(req.params.botId);

    // Get bot info
    const botResult = await query(
      'SELECT * FROM client_bots WHERE id = $1',
      [botId]
    );

    if (botResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        error: 'Bot not found',
      });
    }

    const bot = botResult.rows[0];

    // Check if already running
    if (bot.should_stop === false && bot.status === 'active') {
      return res.status(400).json({
        success: false,
        error: 'Bot is already running',
      });
    }

    // Faqat should_stop flagini false qilamiz va statusni stopped qilamiz
    // Bot daemon har 5 sekundda tekshiradi va ishga tushiradi
    const result = await query(
      `UPDATE client_bots
       SET should_stop = false, status = 'stopped'
       WHERE id = $1
       RETURNING *`,
      [botId]
    );

    console.log(`🚀 Start signal sent to bot ${bot.bot_name} (ID: ${botId})`);

    res.json({
      success: true,
      message: "Ishga tushirish signali yuborildi. Bot 5-10 sekund ichida ishga tushadi.",
      data: { bot: result.rows[0] },
    });
  } catch (error) {
    console.error('Error starting bot:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to start bot',
      message: error.message,
    });
  }
});

// Delete bot
router.delete('/:botId', async (req, res) => {
  try {
    const botId = parseInt(req.params.botId);

    // Get bot info
    const botResult = await query(
      'SELECT * FROM client_bots WHERE id = $1',
      [botId]
    );

    if (botResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        error: 'Bot not found',
      });
    }

    const bot = botResult.rows[0];

    // Kill the process if running
    if (bot.process_id) {
      try {
        exec(`taskkill /F /PID ${bot.process_id}`, (error) => {
          if (error) {
            console.log(`Process ${bot.process_id} may already be stopped`);
          }
        });
      } catch (killError) {
        console.error('Error killing process:', killError);
      }
    }

    // Delete from database
    await query('DELETE FROM client_bots WHERE id = $1', [botId]);

    res.json({
      success: true,
      message: 'Bot deleted successfully',
    });
  } catch (error) {
    console.error('Error deleting bot:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to delete bot',
      message: error.message,
    });
  }
});

export default router;
