const path = require('path')
const fs = require('fs')

const { merge } = require('webpack-merge')
const commonConfig = require('./common.config')
const BundleTracker = require('webpack-bundle-tracker')

config = merge(commonConfig, {
  mode: 'development',
  devtool: 'inline-source-map',
  output: {
    path: path.resolve(__dirname, '../apps/static/bundles_test/'),
    publicPath: '/static/bundles_test/',
    filename: 'js/[name].js',
    chunkFilename: 'js/[name].js',
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

config.plugins.forEach((p, i) => {
  if (p instanceof BundleTracker) {
    config.plugins.splice(
      i,
      1,
      new BundleTracker({
        path: path.resolve(__dirname),
        filename: 'webpack-stats-test.json',
      }),
    )
  }
})

module.exports = config
