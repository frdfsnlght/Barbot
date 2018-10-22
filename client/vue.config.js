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
    }
}
