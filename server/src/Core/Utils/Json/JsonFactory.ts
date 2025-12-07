export default class JsonFactory {
    static createJson(type: String, value: any): String {
        return JSON.stringify({
            type,
            value
        })
    }
}