# Meet the AWS Community

A minimal Hugo static site for showcasing the AWS community members.

## Development

1. Install Hugo: https://gohugo.io/installation/
2. Run the development server:
   ```
   cd meet-aws-community
   hugo server -D
   ```

## Deployment to GitHub Pages

1. Build the site:
   ```
   hugo
   ```

2. Push the contents of the `public` directory to the `gh-pages` branch:
   ```
   cd public
   git init
   git add .
   git commit -m "Deploy to GitHub Pages"
   git branch -M gh-pages
   git remote add origin https://github.com/mzzavaa/meet-aws-community.git
   git push -u origin gh-pages -f
   ```

Alternatively, you can set up a GitHub Action to automate this process.
