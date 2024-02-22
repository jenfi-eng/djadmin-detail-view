const path = require('path')
const fs = require('fs')

const { merge } = require('webpack-merge')
const commonConfig = require('./common.config')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')

module.exports = merge(commonConfig, {
  mode: 'development',
  devtool: 'inline-source-map',
  devServer: {
    port: process.env.PORT || 3000,
    proxy: {
      '*': {
        target: 'https://0.0.0.0:8000',
        secure: false,
      },
    },
    // We need hot=false (Disable HMR) to set liveReload=true
    hot: false,
    liveReload: true,
    server: {
      type: 'https',
      options: {
        key: fs.readFileSync('./docker/support/lvh-key.pem'),
        cert: fs.readFileSync('./docker/support/lvh-cert.pem'),
      },
    },
    allowedHosts: ['lvh.me', '.lvh.me', '.ngrok.io'],
    client: {
      overlay: false,
    },
  },
  module: {
    rules: [
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/i,
        type: 'asset/resource',
      },
    ],
  },
})
