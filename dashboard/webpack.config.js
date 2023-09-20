const CopyWebpackPlugin = require('copy-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const webpack = require('webpack');

const path = require('path');

const PRODUCTION = process.env.PRODUCTION === 'true';
const SERVER_RENDER = process.env.SERVER_RENDER === 'true';

const hash = PRODUCTION ? 'contenthash' : 'hash';

const plugins = [
  new HtmlWebpackPlugin({
    template: PRODUCTION || SERVER_RENDER ? 'src/index.html' : 'src/dev.html',
    chunks: ['index'],
  }),
  new webpack.DefinePlugin({
    react: 'react',
  }),
  new CopyWebpackPlugin({
    patterns: [{ from: path.join(__dirname, 'public'), to: 'assets' }],
  }),
  new webpack.ProvidePlugin({
    React: 'react',
  }),
];

module.exports = {
  mode: PRODUCTION ? 'production' : 'development',
  devtool: PRODUCTION ? 'source-map' : 'eval-cheap-module-source-map',

  entry: { index: './src/index.tsx' },

  output: {
    filename: `assets/[name].[${hash}].js`,
    path: path.resolve(__dirname, 'dist'),
    publicPath: '/',
    chunkFilename: `assets/[id].[${hash}].chunk.js`,
  },

  module: {
    rules: [
      {
        test: /\.(ts|tsx?)$/,
        loader: 'babel-loader',
        exclude: /node_modules/,
      },
    ],
  },

  plugins,

  optimization: {
    moduleIds: 'deterministic',
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
      },
    },
  },

  resolve: {
    extensions: ['.js', '.ts', '.tsx'],
    modules: ['./src', 'node_modules'],
  },

  devServer: {
    port: '4000',
    open: true,
  },
};
