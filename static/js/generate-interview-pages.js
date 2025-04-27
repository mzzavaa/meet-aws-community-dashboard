/**
 * Generate Interview Pages Script
 * 
 * This script reads the AWS_Community_Members.csv file and generates markdown files
 * for each community member with interview data.
 * 
 * Usage: node generate-interview-pages.js
 */

const fs = require('fs');
const path = require('path');
const { parse } = require('csv-parse/sync');

// Configuration
const CSV_PATH = path.join(__dirname, '..', 'data', 'AWS_Community_Members.csv');
const OUTPUT_DIR = path.join(__dirname, '..', 'content', 'interviews');

// Ensure the output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

// Read and parse the CSV file
const csvData = fs.readFileSync(CSV_PATH, 'utf8');
const records = parse(csvData, {
    columns: true,
    skip_empty_lines: true
});

console.log(`Found ${records.length} records in the CSV file`);

// Process each record
records.forEach(record => {
    // Skip records without a name or status
    if (!record.Name || !record.Status) {
        return;
    }
    
    // Create a slug from the name
    const slug = record.Name.toLowerCase()
        .replace(/[^\w\s]/g, '')
        .replace(/\s+/g, '-');
    
    // Determine the roles
    const roles = [];
    if (record['AWS Community Programs'].includes('Heroes')) {
        roles.push('AWS Hero');
    }
    if (record['AWS Community Programs'].includes('Community Builders')) {
        roles.push('AWS Community Builder');
    }
    if (record['AWS Community Programs'].includes('User Group')) {
        roles.push('User Group Leader');
    }
    
    // Extract YouTube link if available
    const youtubeLink = record['Recording date'] || '';
    
    // Create the front matter
    const frontMatter = {
        title: `Meet ${record.Name}: AWS Community Member`,
        name: record.Name,
        roles: roles,
        date: new Date().toISOString().split('T')[0],
        youtube: youtubeLink,
        social: {
            website: '',
            linkedin: '',
            twitter: '',
            github: ''
        },
        status: record.Status,
        featured: record.Status === 'Done',
        questions: {
            career_start: '',
            community_activities: '',
            first_project: '',
            community_touchpoint: '',
            favorite_project: '',
            advice: '',
            online_presence: ''
        }
    };
    
    // Create the content
    const content = `---
title: "${frontMatter.title}"
name: "${frontMatter.name}"
roles: ${JSON.stringify(frontMatter.roles)}
date: ${frontMatter.date}
youtube: "${frontMatter.youtube}"
social:
  website: "${frontMatter.social.website}"
  linkedin: "${frontMatter.social.linkedin}"
  twitter: "${frontMatter.social.twitter}"
  github: "${frontMatter.social.github}"
status: "${frontMatter.status}"
featured: ${frontMatter.featured}
questions:
  career_start: "${frontMatter.questions.career_start}"
  community_activities: "${frontMatter.questions.community_activities}"
  first_project: "${frontMatter.questions.first_project}"
  community_touchpoint: "${frontMatter.questions.community_touchpoint}"
  favorite_project: "${frontMatter.questions.favorite_project}"
  advice: "${frontMatter.questions.advice}"
  online_presence: "${frontMatter.questions.online_presence}"
---

Interview with ${record.Name} coming soon!

${record.Description ? record.Description.replace(/<\/?[^>]+(>|$)/g, '') : ''}
`;
    
    // Write the file
    const outputPath = path.join(OUTPUT_DIR, `${slug}.md`);
    
    // Only write if the file doesn't exist
    if (!fs.existsSync(outputPath)) {
        fs.writeFileSync(outputPath, content);
        console.log(`Created interview page for ${record.Name}`);
    } else {
        console.log(`Interview page for ${record.Name} already exists, skipping`);
    }
});

console.log('Done generating interview pages');
