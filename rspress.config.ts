import { defineConfig } from '@rspress/core';
import path from 'node:path';


export default defineConfig({

    globalStyles: path.join(__dirname, 'theme/var.css'),

    root: 'docs',
    base: '/sailwind_docs/',
    title: 'SailWind',
    description: 'SailWind',
    icon: '/favicon.ico',
    logo:  '/logo.png',
    logoText: 'SailWind',
    lang: "zh",
    i18nSource: {
        outlineTitle: { zh: '本页目录' },
        prevPageText: { zh: '上一页' },
        nextPageText: { zh: '下一页' },
        lastUpdatedText: { zh: '最近更新时间' },
        searchPlaceholderText: { zh: '搜索' },
        sourceCodeText: { zh: '源码' },
        'overview.filterNameText': { zh: '快速查找' },
        'overview.filterPlaceholderText': { zh: '输入关键词' },
        'overview.filterNoResultText': { zh: '未查询到结果' },
    },
    themeConfig: {
        editLink: {
            docRepoBaseUrl: 'http://10.0.21.144:8000/editor/6e301d3c-d9c8-4944-bfa2-cc2a197c858f/docs',
        },
        enableContentAnimation: true,
        enableAppearanceAnimation: true,
        enableScrollToTop: true,
        lastUpdated: true,
        socialLinks: [
            {
                icon: 'github',
                mode: 'link',
                content: 'https://github.com/mikigo/sailwind_docs/',
            }
        ],

        footer: {
            message: `版权所有 © 2023-${new Date().getFullYear()} 派兹互连`,
        },
        hideNavbar: 'auto',
    },
});