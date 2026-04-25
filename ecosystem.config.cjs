module.exports = {
  apps: [
    {
      name: "buildup-flask",
      script: "python",
      args: "-m flask run --host=0.0.0.0 --port=5000",
      cwd: "C:/Users/Anmol/OneDrive/Desktop/B",
      exec_mode: "fork",
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "500M",
      env: {
        FLASK_APP: "app.py",
        PORT: "5000",
        NODE_ENV: "development"
      },
      log_file: "./logs/buildup-flask.log",
      out_file: "./logs/buildup-flask-out.log",
      error_file: "./logs/buildup-flask-error.log",
      merge_logs: true,
      time: true
    },
    {
      name: "skillup-backend",
      script: "node",
      args: "node_modules/tsx/dist/cli.mjs src/index.ts",
      cwd: "C:/Users/Anmol/OneDrive/Desktop/B/coding-portal/backend",
      exec_mode: "fork",
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "500M",
      env: {
        NODE_ENV: "development"
      },
      log_file: "./logs/skillup-backend.log",
      out_file: "./logs/skillup-backend-out.log",
      error_file: "./logs/skillup-backend-error.log",
      merge_logs: true,
      time: true
    },
    {
      name: "skillup-judge",
      script: "node",
      args: "node_modules/tsx/dist/cli.mjs src/index.ts",
      cwd: "C:/Users/Anmol/OneDrive/Desktop/B/coding-portal/judge",
      exec_mode: "fork",
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "300M",
      env: {
        NODE_ENV: "development"
      },
      log_file: "./logs/skillup-judge.log",
      out_file: "./logs/skillup-judge-out.log",
      error_file: "./logs/skillup-judge-error.log",
      merge_logs: true,
      time: true
    },
    {
      name: "skillup-frontend",
      script: "node",
      args: "node_modules/vite/bin/vite.js",
      cwd: "C:/Users/Anmol/OneDrive/Desktop/B/coding-portal/frontend",
      exec_mode: "fork",
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "500M",
      env: {
        NODE_ENV: "development"
      },
      log_file: "./logs/skillup-frontend.log",
      out_file: "./logs/skillup-frontend-out.log",
      error_file: "./logs/skillup-frontend-error.log",
      merge_logs: true,
      time: true
    }
  ]
};

