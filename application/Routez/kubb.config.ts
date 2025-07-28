import { pluginOas } from '@kubb/plugin-oas'
import { pluginClient } from '@kubb/plugin-client'
import { pluginTs } from '@kubb/plugin-ts'
import { defineConfig } from '@kubb/core'
import { enviorment } from './enviorment'

export default defineConfig(() => ({
    input: { path: enviorment.API_SWAGGER },
    output: { path: './src/api' },
    plugins: [
        pluginOas(),
        pluginTs({ output: { path: 'models' } }),
        pluginClient({
            output: { path: 'client' },
            client: 'axios',
            baseURL: enviorment.API,
        }),
    ],
}))