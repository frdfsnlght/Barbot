const GitRevisionPlugin = require('git-revision-webpack-plugin')
const gitRevisionPlugin = new GitRevisionPlugin({branch: true})
const ReplacePlugin = require('webpack-plugin-replace')

module.exports = {
    devServer: {
        port: 8081
    },
    chainWebpack: config => {
        config.module
            .rule('vue')
            .use('vue-loader')
                .loader('vue-loader')
                .tap(options => {
                    options.transformAssetUrls = {
                        audio: 'src'
                    }
                    return options
                })
        config.module
            .rule('graphql')
            .test(/\.graphql$/)
            .use('graphql-tag/loader')
                .loader('graphql-tag/loader')
                .end()
    },
    configureWebpack: {
        plugins: [
            new ReplacePlugin({
                include: 'src/build.js',
                values: {
                    'GIT_VERSION': gitRevisionPlugin.version(),
                    'GIT_COMMITHASH': gitRevisionPlugin.commithash(),
                    'GIT_BRANCH': gitRevisionPlugin.branch(),
                    'BUILD_DATE': (new Date()).toLocaleString(),
                }
            }),            
        ],
    },
}
