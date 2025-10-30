require('dotenv').config();

module.exports = {
    // Telegram configuration
    botToken: process.env.BOT_TOKEN,
    ownerId: process.env.OWNER_ID,

    // Proxy configuration (optional)
    proxyUrl: process.env.PROXY_URL || null,
    apiRoot: process.env.API_ROOT || 'https://api.telegram.org',

    // Local client configuration
    clientUrl: process.env.CLIENT_URL || 'http://127.0.0.1:5000',
    authToken: process.env.AUTH_TOKEN,

    // Request settings
    requestTimeout: parseInt(process.env.REQUEST_TIMEOUT) || 10000,
};