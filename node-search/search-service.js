// MiniAI/node-search/search-service.js 完整修复版
const axios = require('axios');
const cheerio = require('cheerio');

// 【关键修复】函数定义在最外层，确保全局可访问
function extractKeywords(question) {
    if (!question || typeof question !== 'string') {
        return [];
    }
    // 过滤特殊字符，仅保留中文/字母
    const cleanContent = question.replace(/[^\u4e00-\u9fa5a-zA-Z]/g, ' ');
    // 分割为单词，过滤长度<2的无效词
    const rawKeywords = cleanContent.split(' ').filter(word => word.length >= 2);
    // 去重
    const uniqueKeywords = [...new Set(rawKeywords)];
    return uniqueKeywords;
}

async function searchAnswer(question) {
    try {
        // 调用extractKeywords（此时函数已定义）
        const keywords = extractKeywords(question);
        if (keywords.length === 0) {
            return {
                success: false,
                message: "未提取到有效关键词",
                data: [],
                keywords: []
            };
        }

        const encodeKeywords = encodeURIComponent(keywords.join(' '));
        const response = await axios.get(
            `https://cn.bing.com/search?q=${encodeKeywords}&count=5`,
            {
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                },
                timeout: 10000
            }
        );

        const $ = cheerio.load(response.data);
        const results = [];
        $('#b_results .b_algo').each((index, element) => {
            const title = $(element).find('h2').text().trim();
            const link = $(element).find('a').attr('href');
            const summary = $(element).find('.b_caption p').text().trim();
            if (title && link && summary) {
                results.push({ title, link, summary });
            }
        });

        return {
            success: results.length > 0,
            message: results.length > 0 ? "找到相关搜索结果" : "未找到有效信息",
            data: results,
            keywords: keywords
        };
    } catch (error) {
        return {
            success: false,
            message: `搜索失败：${error.message || '未知错误'}`,
            data: [],
            keywords: []
        };
    }
}

// 接收外部参数
const userQuestion = process.argv[2];
if (!userQuestion) {
    console.log(JSON.stringify({
        success: false,
        message: "未传入用户问题",
        data: [],
        keywords: []
    }));
    process.exit(1);
}

// 执行搜索并输出
searchAnswer(userQuestion)
    .then(result => console.log(JSON.stringify(result)))
    .catch(err => console.log(JSON.stringify({
        success: false,
        message: `执行失败：${err.message}`,
        data: [],
        keywords: []
    })));