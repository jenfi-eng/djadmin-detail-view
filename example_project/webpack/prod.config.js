const { merge } = require('webpack-merge')
const commonConfig = require('./common.config')

// This variable should mirror the one from config/settings/production.py
const staticUrl = '/static/'

module.exports = merge(commonConfig, {
  mode: 'production',
  devtool: 'source-map',
  bail: true,
  output: {
    publicPath: '',
  },
  module: {
    rules: [
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/i,
        type: 'asset/resource',
        generator: {
          filename: './fonts/[name]-[hash][ext]',
          outputPath: './css',

          //
          // TODO: See if this ever doesn't produce the doubleslash - ..//fonts/[filename].woff problem.
          // rm -rf staticfiles;  rm -rf apps/static/bundles; yarn build; ./manage.py collectstatic; grep "bdb9e23299f9d1320a8b" -R staticfiles
          // Above sticks all the fonts inside the ./css directory because I can't put them in a sibling dir and reference them.
          //
          // filename: '../fonts/[name]-[hash][ext]',
          // outputPath: './fonts',
        },
      },
      {
        test: /\.(png|svg|jpg|jpeg|gif)$/i,
        type: 'asset/resource',
        generator: {
          filename: './[name]-[hash][ext]',
          outputPath: './css',

          // This is stupid, it puts the svgs in the css directory because Justin can't figure out how to keep them spearated while properly
          // referencing them from the css.
        },
      },
    ],
  },
})
