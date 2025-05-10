# AWS Community Dashboard

A comprehensive dashboard for visualizing and exploring the AWS community, including AWS Heroes, Community Builders, and User Groups worldwide.

**Created by [Linda Mohamed](https://www.linkedin.com/in/lindamohamed/), AWS Hero from Austria**

## Project Overview

The AWS Community Dashboard is a web-based platform that provides an interactive way to explore the global AWS community. It features:

- Interactive maps showing AWS Heroes, Community Builders, and User Groups worldwide
- Detailed profiles and information about community members
- Filtering capabilities by category, region, and more
- Interview highlights with community members
- Comprehensive statistics about the AWS community

## Directory Structure

```
meet-aws-community-dashboard/
├── archetypes/                  # Hugo archetypes for content generation
├── content/                     # Content files (markdown)
│   ├── interviews/              # Interview content with AWS Heroes and Community Builders
│   └── posts/                   # Blog posts about AWS community events
├── data/                        # Data files used by Hugo templates
├── layouts/                     # HTML templates
│   ├── _default/                # Default templates
│   │   ├── baseof.html             # Base template with common elements
│   │   ├── community-builders.html  # Community Builders page template
│   │   ├── heroes.html             # AWS Heroes page template
│   │   ├── list.html               # List template for content sections
│   │   ├── single.html             # Single page template for content
│   │   └── user-groups.html        # User Groups page template
│   ├── partials/                # Reusable template parts
│   │   ├── footer.html             # Site footer
│   │   ├── head.html               # Document head with meta tags
│   │   ├── header.html             # Site header with navigation
│   │   └── scripts.html            # Common JavaScript includes
│   └── index.html               # Homepage template
├── static/                      # Static assets
│   ├── css/                     # CSS stylesheets
│   │   ├── community-components.css  # Main component styles
│   │   ├── dark-mode.css            # Dark mode specific styles
│   │   └── map-markers.css          # Map-specific styles
│   ├── data/                    # Data files for the dashboard
│   │   ├── aws_community_builders.csv  # Community Builders data
│   │   ├── aws_heroes.csv             # AWS Heroes data
│   │   └── aws_user_groups_with_members.csv  # User Groups data with member counts
│   ├── images/                  # Image assets
│   │   ├── heroes/                 # AWS Hero profile images
│   │   ├── builders/              # Community Builder profile images
│   │   ├── logos/                 # Logo images for various purposes
│   │   └── icons/                 # Icon images for UI elements
│   └── js/                      # JavaScript files
│       ├── dark-mode.js           # Dark mode toggle functionality
│       ├── map-config.js          # Map configuration and utilities
│       └── filters.js             # Search and filtering functionality
├── config.toml                  # Hugo configuration
└── README.md                    # Project documentation
```

Here’s the fully updated **Data Sources and Collection** section for your `README.md`, including details on longitude/latitude geocoding, member count enrichment, and data cleaning:

---

## Data Sources and Collection

This dashboard integrates data from AWS Community programs using a combination of scraping, API calls, and transformation scripts. The datasets are cleaned, enriched with geographic coordinates, and exported as CSV files for further use in dashboards or visualizations.

### 1. **AWS Community Builders**
- Data is collected using a script that queries an internal AWS website search endpoint (not an official public API).
- Two paginated queries are made to retrieve all entries:
  - First 2,000 records sorted A–Z
  - Remaining records sorted Z–A
- Extracted fields:
  - Name
  - Location (usually city or country)
  - Program category
  - Public bio/profile link
- **Latitude and longitude** are added using the `geopy` library with the **Nominatim geocoding service** to convert text-based locations into coordinates.
- The final cleaned and geocoded dataset is saved as `community_builders_complete.csv`.

### 2. **AWS User Groups (Meetup.com)**
- Event and group data is processed from a structured JSON response (typically exported from the Meetup GraphQL API).
- Extracted fields include:
  - Event title, date, location
  - Venue city and country
  - RSVP/“going” count
- **Member count** per user group is added manually or via pre-processed API data.
- Latitude and longitude may also be geocoded from venue city/country if not included.
- The result is saved as `meetup_similar_events.csv`.

### 3. **AWS Heroes**
- Data is either manually collected or scraped from the [AWS Heroes Directory](https://aws.amazon.com/developer/community/heroes/).
- Extracted fields:
  - Name, Hero category, location
  - Profile URL and image
- **Geolocation is applied** to convert the location field into latitude and longitude for mapping.
- Output is transformed and aligned with other data sources for integration.

---

### 🧹 Data Cleaning and Enrichment
Across all sources:
- Entries with missing or malformed data are filtered out (e.g., empty names or locations).
- Locations are normalized before geocoding (e.g., trimming whitespace, consistent formatting).
- For duplicates or edge cases (e.g., multiple same names), basic disambiguation may be applied.
- Only structured fields relevant for display and mapping are retained.

> ⚠️ **Note:** The data sources use internal search endpoints and external APIs. These may change without notice and are not officially supported by AWS or Meetup. This project and all associated data or outputs are intended solely for community or personal use and may not be used for commercial purposes.

## Features

### Maps

- Interactive world map on the homepage showing all community members
- Dedicated maps for Heroes, Community Builders, and User Groups
- Clustering for areas with many community members
- Popup information cards with details about each community member/group
- Profile images for AWS Heroes
- Member counts for User Groups on Meetup.com

### Filtering and Search

- Filter by category (Machine Learning, Serverless, etc.)
- Search by name, location, or category
- Region-specific filtering for User Groups
- Special handling for Machine Learning category to include related terms

### Responsive Design

- Works on desktop and mobile devices
- Dark mode support with proper color contrast
- Adaptive layout for different screen sizes

## Setup and Development

### Prerequisites

- [Hugo](https://gohugo.io/) (Extended version)
- Basic knowledge of HTML, CSS, and JavaScript
- Git for version control

### Local Development

1. Clone the repository:
   ```
   git clone https://github.com/mzzavaa/meet-the-aws-community-dashboard.git
   cd meet-the-aws-community-dashboard
   ```

2. Start the Hugo development server:
   ```
   hugo server -D
   ```

3. Open your browser and navigate to `http://localhost:1313`

### Updating Data

The data files are located in the `static/data/` directory:

- `aws_heroes.csv`: AWS Heroes data
- `aws_community_builders.csv`: Community Builders data
- `aws_user_groups_with_members.csv`: User Groups data with member counts

To update the data, simply edit these CSV files. The format should be maintained as follows:

#### AWS Heroes CSV Format
```
Name,Location,Category,Bio URL,Image URL,Latitude,Longitude,Status
```

#### Community Builders CSV Format
```
Name,Location,Category,Bio URL,Latitude,Longitude
```

#### User Groups CSV Format
```
Name,Location,URL,Category,Latitude,Longitude,Platform,Members
```

### Adding New Content

1. To add a new interview:
   ```
   hugo new content/interviews/person-name.md
   ```

2. To add a new blog post:
   ```
   hugo new content/posts/post-title.md
   ```

3. Edit the created markdown files with your content

## Deployment

The site can be deployed to any static hosting service:

1. Build the site:
   ```
   hugo --minify
   ```

2. Deploy the contents of the `public` directory to your hosting service

### Deployment Options

- **AWS Amplify**: Easy deployment with Git integration
- **AWS S3 + CloudFront**: Cost-effective hosting with global CDN
- **GitHub Pages**: Free hosting for open-source projects
- **Netlify/Vercel**: Modern hosting platforms with CI/CD

## Future Enhancements

- Full automation of data collection through AWS APIs and web scraping
- Enhanced filtering options with more granular categories
- More detailed profiles with additional information
- Integration with AWS events calendar
- User Group leader information display
- Additional community statistics and visualizations
- Improved mobile experience
- Internationalization support

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- AWS for supporting the global community and providing the public data
- All AWS Heroes, Community Builders, and User Group leaders for their contributions
- The Hugo community for the excellent static site generator
- [Linda Mohamed](https://www.linkedin.com/in/linda-mohamed/), AWS Hero from Austria, for creating and maintaining this project
