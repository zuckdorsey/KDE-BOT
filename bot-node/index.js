const { Telegraf, Markup } = require('telegraf');
const axios = require('axios');
require('dotenv').config();

// ===========================
// CONFIGURATION
// ===========================

const BOT_TOKEN = process.env.BOT_TOKEN;
const OWNER_ID = process.env.OWNER_ID;
const CLIENT_URL = process.env.CLIENT_URL || 'http://127.0.0.1:5000';
const AUTH_TOKEN = process.env.AUTH_TOKEN;
const TIMEOUT = parseInt(process.env.REQUEST_TIMEOUT) || 30000;

if (!BOT_TOKEN || !OWNER_ID || !AUTH_TOKEN) {
  console.error('❌ Missing required .env variables: BOT_TOKEN, OWNER_ID, AUTH_TOKEN');
  process.exit(1);
}

console.log('🚀 Starting Telegram Bot with Buttons...');
console.log(`👤 Owner: ${OWNER_ID}`);
console.log(`🔗 Client: ${CLIENT_URL}`);
console.log(`🔑 Auth: ${AUTH_TOKEN.substring(0, 10)}...${AUTH_TOKEN.slice(-5)}\n`);

// ===========================
// INITIALIZE BOT & CLIENT
// ===========================

const bot = new Telegraf(BOT_TOKEN);

const client = axios.create({
  baseURL: CLIENT_URL,
  timeout: TIMEOUT,
  headers: {
    'Authorization': `Bearer ${AUTH_TOKEN}`,
    'Content-Type': 'application/json'
  }
});

// ===========================
// MIDDLEWARE - AUTH CHECK
// ===========================

bot.use((ctx, next) => {
  const userId = ctx.from?.id.toString();
  if (userId !== OWNER_ID) {
    console.log(`⚠️ Unauthorized access from ${userId}`);
    return ctx.reply('❌ Unauthorized');
  }
  return next();
});

// ===========================
// KEYBOARD LAYOUTS
// ===========================

// Main Menu Keyboard
const mainMenu = Markup.inlineKeyboard([
  [
    Markup.button.callback('🖥️ System', 'menu_system'),
    Markup.button.callback('🔊 Media', 'menu_media')
  ],
  [
    Markup.button.callback('📋 Clipboard', 'menu_clipboard'),
    Markup.button.callback('📁 Files', 'menu_files')
  ],
  [
    Markup.button.callback('ℹ️ Status', 'cmd_status'),
    Markup.button.callback('🔄 Refresh', 'menu_main')
  ]
]);

// System Menu
const systemMenu = Markup.inlineKeyboard([
  [
    Markup.button.callback('🔒 Lock Screen', 'cmd_lock'),
    Markup.button.callback('😴 Sleep', 'cmd_sleep')
  ],
  [
    Markup.button.callback('📸 Screenshot', 'cmd_screenshot'),
    Markup.button.callback('⚠️ Shutdown', 'cmd_shutdown_warn')
  ],
  [Markup.button.callback('« Back to Menu', 'menu_main')]
]);

// Media Menu
const mediaMenu = Markup.inlineKeyboard([
  [
    Markup.button.callback('🔇 Mute', 'cmd_mute'),
    Markup.button.callback('🔉 Volume 25%', 'cmd_vol_25')
  ],
  [
    Markup.button.callback('🔉 Volume 50%', 'cmd_vol_50'),
    Markup.button.callback('🔊 Volume 75%', 'cmd_vol_75')
  ],
  [
    Markup.button.callback('🔊 Volume 100%', 'cmd_vol_100'),
    Markup.button.callback('« Back', 'menu_main')
  ]
]);

// Clipboard Menu
const clipboardMenu = Markup.inlineKeyboard([
  [
    Markup.button.callback('📋 Get Clipboard', 'cmd_paste'),
    Markup.button.callback('✍️ Copy Text', 'cmd_copy_prompt')
  ],
  [Markup.button.callback('« Back to Menu', 'menu_main')]
]);

// Files Menu
const filesMenu = Markup.inlineKeyboard([
  [
    Markup.button.callback('📤 Upload File', 'cmd_upload_prompt'),
    Markup.button.callback('📥 Download File', 'cmd_download_prompt')
  ],
  [Markup.button.callback('« Back to Menu', 'menu_main')]
]);

// Shutdown Confirmation
const shutdownConfirm = Markup.inlineKeyboard([
  [
    Markup.button.callback('✅ Yes, Shutdown', 'cmd_shutdown'),
    Markup.button.callback('❌ Cancel', 'menu_system')
  ]
]);

// ===========================
// COMMAND HANDLERS
// ===========================

// Start command - Show main menu
bot.command('start', (ctx) => {
  ctx.reply(
    '🤖 *KDE Connect Bot*\n\n' +
    'Control your PC via Telegram with buttons!\n\n' +
    'Choose a category below:',
    {
      parse_mode: 'Markdown',
      ...mainMenu
    }
  );
});

// Menu command - Show main menu
bot.command('menu', (ctx) => {
  ctx.reply(
    '📱 *Main Menu*\n\nSelect an option:',
    {
      parse_mode: 'Markdown',
      ...mainMenu
    }
  );
});

// Help command
bot.command('help', (ctx) => {
  ctx.reply(
    '📖 *Help & Commands*\n\n' +
    '*Text Commands:*\n' +
    '/start - Show main menu\n' +
    '/menu - Show main menu\n' +
    '/status - System status\n' +
    '/volume <0-100> - Set volume\n' +
    '/copy <text> - Copy text\n' +
    '/help - Show this help\n\n' +
    '*Button Interface:*\n' +
    'Use the interactive buttons for easier control!\n\n' +
    '*File Operations:*\n' +
    'Send any file to upload to PC\n' +
    'Use Files menu to download',
    { parse_mode: 'Markdown' }
  );
});

// Status command (also available via button)
bot.command('status', async (ctx) => {
  await handleStatus(ctx);
});

// Volume command (text version)
bot.command('volume', async (ctx) => {
  const level = parseInt(ctx.message.text.split(' ')[1]);
  if (isNaN(level) || level < 0 || level > 100) {
    return ctx.reply('❌ Usage: /volume 50 (0-100)', mediaMenu);
  }
  await sendCmd(ctx, 'volume', { level }, false);
});

// Copy command (text version)
bot.command('copy', async (ctx) => {
  const text = ctx.message.text.replace('/copy', '').trim();
  if (!text) return ctx.reply('❌ Usage: /copy your text here', clipboardMenu);
  await sendCmd(ctx, 'copy', { text }, false);
});

// ===========================
// CALLBACK QUERY HANDLERS (BUTTONS)
// ===========================

// Main menu navigation
bot.action('menu_main', (ctx) => {
  ctx.editMessageText(
    '📱 *Main Menu*\n\nSelect an option:',
    {
      parse_mode: 'Markdown',
      ...mainMenu
    }
  ).catch(() => ctx.reply('📱 Main Menu', mainMenu));
});

bot.action('menu_system', (ctx) => {
  ctx.editMessageText(
    '🖥️ *System Control*\n\nChoose an action:',
    {
      parse_mode: 'Markdown',
      ...systemMenu
    }
  );
});

bot.action('menu_media', (ctx) => {
  ctx.editMessageText(
    '🔊 *Media Control*\n\nAdjust volume or mute:',
    {
      parse_mode: 'Markdown',
      ...mediaMenu
    }
  );
});

bot.action('menu_clipboard', (ctx) => {
  ctx.editMessageText(
    '📋 *Clipboard Manager*\n\nManage clipboard:',
    {
      parse_mode: 'Markdown',
      ...clipboardMenu
    }
  );
});

bot.action('menu_files', (ctx) => {
  ctx.editMessageText(
    '📁 *File Manager*\n\nFile operations:',
    {
      parse_mode: 'Markdown',
      ...filesMenu
    }
  );
});

// System commands
bot.action('cmd_lock', (ctx) => {
  ctx.answerCbQuery('🔒 Locking screen...');
  sendCmd(ctx, 'lock', {}, true);
});

bot.action('cmd_sleep', (ctx) => {
  ctx.answerCbQuery('😴 Putting PC to sleep...');
  sendCmd(ctx, 'sleep', {}, true);
});

bot.action('cmd_screenshot', async (ctx) => {
  ctx.answerCbQuery('📸 Taking screenshot...');
  await handleScreenshot(ctx);
});

bot.action('cmd_shutdown_warn', (ctx) => {
  ctx.editMessageText(
    '⚠️ *SHUTDOWN WARNING*\n\n' +
    'Are you sure you want to shutdown your PC?\n\n' +
    'This action cannot be undone!',
    {
      parse_mode: 'Markdown',
      ...shutdownConfirm
    }
  );
});

bot.action('cmd_shutdown', (ctx) => {
  ctx.answerCbQuery('⚠️ Shutting down...');
  sendCmd(ctx, 'shutdown', {}, true);
});

// Media commands
bot.action('cmd_mute', (ctx) => {
  ctx.answerCbQuery('🔇 Toggling mute...');
  sendCmd(ctx, 'mute', {}, true);
});

bot.action('cmd_vol_25', (ctx) => {
  ctx.answerCbQuery('🔉 Setting volume to 25%...');
  sendCmd(ctx, 'volume', { level: 25 }, true);
});

bot.action('cmd_vol_50', (ctx) => {
  ctx.answerCbQuery('🔉 Setting volume to 50%...');
  sendCmd(ctx, 'volume', { level: 50 }, true);
});

bot.action('cmd_vol_75', (ctx) => {
  ctx.answerCbQuery('🔊 Setting volume to 75%...');
  sendCmd(ctx, 'volume', { level: 75 }, true);
});

bot.action('cmd_vol_100', (ctx) => {
  ctx.answerCbQuery('🔊 Setting volume to 100%...');
  sendCmd(ctx, 'volume', { level: 100 }, true);
});

// Clipboard commands
bot.action('cmd_paste', async (ctx) => {
  ctx.answerCbQuery('📋 Getting clipboard...');
  await handlePaste(ctx);
});

bot.action('cmd_copy_prompt', (ctx) => {
  ctx.answerCbQuery();
  ctx.reply(
    '✍️ *Copy Text to Clipboard*\n\n' +
    'Send me the text you want to copy:\n\n' +
    'Example: `Hello World`\n' +
    'Or use: `/copy your text here`',
    { parse_mode: 'Markdown', ...clipboardMenu }
  );
});

// File commands
bot.action('cmd_upload_prompt', (ctx) => {
  ctx.answerCbQuery();
  ctx.reply(
    '📤 *Upload File to PC*\n\n' +
    'Send me any file (document, image, video, etc.) and I will save it to your PC.',
    { parse_mode: 'Markdown', ...filesMenu }
  );
});

bot.action('cmd_download_prompt', (ctx) => {
  ctx.answerCbQuery();
  ctx.reply(
    '📥 *Download File from PC*\n\n' +
    'Send the full file path:\n\n' +
    'Example:\n' +
    '`/home/user/document.pdf`\n' +
    '`C:\\Users\\user\\file.txt`',
    { parse_mode: 'Markdown', ...filesMenu }
  );
});

// Status command
bot.action('cmd_status', async (ctx) => {
  ctx.answerCbQuery('🔍 Checking system...');
  await handleStatus(ctx);
});

// ===========================
// MESSAGE HANDLERS
// ===========================

// Handle file uploads
bot.on('document', async (ctx) => {
  const msg = await ctx.reply('📥 Uploading file to PC...', mainMenu);
  try {
    const file = await ctx.telegram.getFile(ctx.message.document.file_id);
    const url = `https://api.telegram.org/file/bot${BOT_TOKEN}/${file.file_path}`;
    
    const res = await client.post('/upload', {
      filename: ctx.message.document.file_name,
      url: url,
      size: ctx.message.document.file_size
    });
    
    await ctx.telegram.editMessageText(
      ctx.chat.id,
      msg.message_id,
      null,
      `✅ *File Uploaded*\n\n📁 ${res.data.path}`,
      { parse_mode: 'Markdown', ...mainMenu }
    );
  } catch (err) {
    handleError(ctx, err, msg.message_id);
  }
});

// Handle text messages (for copy and file path)
bot.on('text', async (ctx) => {
  const text = ctx.message.text;
  
  // Ignore commands
  if (text.startsWith('/')) return;
  
  // Check if it looks like a file path
  if (text.includes('/') || text.includes('\\')) {
    const msg = await ctx.reply('📥 Retrieving file from PC...', mainMenu);
    try {
      const res = await client.post('/getfile', { path: text }, { responseType: 'stream' });
      await ctx.replyWithDocument(
        { source: res.data, filename: require('path').basename(text) },
        mainMenu
      );
      await ctx.telegram.deleteMessage(ctx.chat.id, msg.message_id);
    } catch (err) {
      handleError(ctx, err, msg.message_id);
    }
  } else {
    // Assume it's text to copy
    await sendCmd(ctx, 'copy', { text }, false);
  }
});

// Handle photos (save to PC)
bot.on('photo', async (ctx) => {
  const msg = await ctx.reply('📸 Saving photo to PC...', mainMenu);
  try {
    const photo = ctx.message.photo[ctx.message.photo.length - 1];
    const file = await ctx.telegram.getFile(photo.file_id);
    const url = `https://api.telegram.org/file/bot${BOT_TOKEN}/${file.file_path}`;
    
    const filename = `photo_${Date.now()}.jpg`;
    const res = await client.post('/upload', { filename, url, size: photo.file_size });
    
    await ctx.telegram.editMessageText(
      ctx.chat.id,
      msg.message_id,
      null,
      `✅ *Photo Saved*\n\n📁 ${res.data.path}`,
      { parse_mode: 'Markdown', ...mainMenu }
    );
  } catch (err) {
    handleError(ctx, err, msg.message_id);
  }
});

// ===========================
// HELPER FUNCTIONS
// ===========================

async function sendCmd(ctx, command, params = {}, isCallback = false) {
  let msg;
  if (!isCallback) {
    msg = await ctx.reply('⏳ Processing...');
  }
  
  try {
    const res = await client.post('/command', { command, params });
    const icon = res.data.status === 'success' ? '✅' : '❌';
    const responseText = `${icon} ${res.data.message}`;
    
    if (isCallback) {
      await ctx.editMessageText(responseText, mainMenu);
    } else {
      await ctx.telegram.editMessageText(ctx.chat.id, msg.message_id, null, responseText, mainMenu);
    }
  } catch (err) {
    handleError(ctx, err, msg?.message_id, isCallback);
  }
}

async function handleStatus(ctx) {
  try {
    const res = await client.get('/status');
    const d = res.data;
    const statusText = 
      `✅ *System Online*\n\n` +
      `🖥️ Host: \`${d.hostname}\`\n` +
      `💻 OS: \`${d.os}\`\n` +
      `📊 CPU: \`${d.cpu}%\`\n` +
      `💾 RAM: \`${d.memory}%\`\n` +
      `⏱️ Uptime: \`${d.uptime}\``;
    
    if (ctx.callbackQuery) {
      await ctx.editMessageText(statusText, { parse_mode: 'Markdown', ...mainMenu });
    } else {
      await ctx.reply(statusText, { parse_mode: 'Markdown', ...mainMenu });
    }
  } catch (err) {
    handleError(ctx, err);
  }
}

async function handlePaste(ctx) {
  try {
    const res = await client.post('/command', { command: 'paste' });
    const content = res.data.content || '(empty)';
    const text = `📋 *Clipboard Content:*\n\n\`\`\`\n${content}\n\`\`\``;
    
    await ctx.editMessageText(text, { parse_mode: 'Markdown', ...clipboardMenu });
  } catch (err) {
    handleError(ctx, err);
  }
}

async function handleScreenshot(ctx) {
  try {
    const res = await client.post('/command', { command: 'screenshot' });
    if (res.data.status === 'success' && res.data.file) {
      const fileRes = await client.get(`/download/${res.data.file}`, { responseType: 'stream' });
      await ctx.replyWithPhoto({ source: fileRes.data }, systemMenu);
      if (ctx.callbackQuery) {
        await ctx.deleteMessage();
      }
    }
  } catch (err) {
    handleError(ctx, err);
  }
}

function handleError(ctx, err, msgId = null, isCallback = false) {
  console.error('❌ Error:', err.message);
  
  let msg = '❌ *Error*\n\n';
  if (err.code === 'ECONNREFUSED') {
    msg += 'Python client not running!\n\nStart it:\n`cd client && python server.py`';
  } else if (err.response?.status === 401) {
    msg += 'AUTH_TOKEN mismatch!\n\nCheck .env files in bot/ and client/';
  } else if (err.code === 'ECONNRESET') {
    msg += 'Connection reset. Please try again.';
  } else {
    msg += err.message;
  }
  
  if (isCallback && ctx.callbackQuery) {
    ctx.editMessageText(msg, { parse_mode: 'Markdown', ...mainMenu }).catch(() => {
      ctx.reply(msg, { parse_mode: 'Markdown', ...mainMenu });
    });
  } else if (msgId) {
    ctx.telegram.editMessageText(ctx.chat.id, msgId, null, msg, { parse_mode: 'Markdown', ...mainMenu })
      .catch(() => ctx.reply(msg, { parse_mode: 'Markdown', ...mainMenu }));
  } else {
    ctx.reply(msg, { parse_mode: 'Markdown', ...mainMenu });
  }
}

// ===========================
// START BOT
// ===========================

bot.launch()
  .then(() => {
    console.log('✅ Bot started successfully with interactive buttons!');
    console.log('📡 Long polling active');
    console.log('📱 Send /start to your bot on Telegram\n');
  })
  .catch((err) => {
    console.error('❌ Failed to start bot:', err.message);
    process.exit(1);
  });

// Graceful shutdown
process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));