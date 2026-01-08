import fs from 'node:fs'
import path from 'node:path'

export default defineEventHandler(async (event) => {
    try {
        // Navigate up from iot/operator-indicator/server/api/status.get.ts
        // to repository root to find json_reference.json
        // process.cwd() is likely iot/operator-indicator/.
        const filePath = path.resolve(process.cwd(), '../../json_reference.json')

        if (!fs.existsSync(filePath)) {
            throw createError({
                statusCode: 404,
                statusMessage: 'json_reference.json not found',
            })
        }

        const fileContent = fs.readFileSync(filePath, 'utf-8')
        const json = JSON.parse(fileContent)

        return json
    } catch (error) {
        console.error('Error reading json_reference.json:', error)
        throw createError({
            statusCode: 500,
            statusMessage: 'Failed to read status file',
        })
    }
})
