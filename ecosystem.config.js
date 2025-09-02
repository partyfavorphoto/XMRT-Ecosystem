module.exports = {
  apps: [
    {
      name: 'xmrt-enhanced-dao',
      script: 'enhanced_main_with_mcp.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production',
        PORT: 5000,
        HOST: '0.0.0.0',
        FLASK_ENV: 'production',
        GITHUB_PERSONAL_ACCESS_TOKEN: process.env.GITHUB_PERSONAL_ACCESS_TOKEN || '',
        OPENAI_API_KEY: process.env.OPENAI_API_KEY || '',
        SECRET_KEY: 'xmrt-ecosystem-mcp-secret-2025',
        LOCAL_MCP_ENABLED: 'false',
        MCP_SERVER_URL: 'https://api.githubcopilot.com/mcp/'
      },
      env_production: {
        NODE_ENV: 'production',
        PORT: 5000,
        FLASK_ENV: 'production'
      },
      log_file: './logs/xmrt-combined.log',
      out_file: './logs/xmrt-out.log',
      error_file: './logs/xmrt-error.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      time: true
    },
    {
      name: 'xmrt-legacy-system',
      script: 'main.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '512M',
      env: {
        NODE_ENV: 'production',
        PORT: 5001,
        HOST: '0.0.0.0',
        FLASK_ENV: 'production'
      },
      log_file: './logs/xmrt-legacy-combined.log',
      out_file: './logs/xmrt-legacy-out.log', 
      error_file: './logs/xmrt-legacy-error.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      time: true
    }
  ]
};