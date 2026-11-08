// Edit these values to rename and describe your site.
export const SITE = {
  name: 'Tech Notes',
  tagline: 'Practical Linux, cybersecurity and tech guides',
  description:
    'Clear, practical guides on Linux, defensive cybersecurity, networking and self-hosting.',
  author: 'Tech Notes Editorial',
  email: '', // optional: shown on the editorial policy page for corrections
  lang: 'en',
  postsPerPage: 20,
  // Google AdSense. Leave client empty until your account is approved.
  // client looks like 'ca-pub-1234567890123456'. Slot IDs come from AdSense > Ads > By ad unit.
  // With only the client set, Auto ads handle placement; manual slots below are optional.
  adsense: {
    client: '',
    slots: { top: '', bottom: '', sidebar: '' } as Record<string, string>,
  },
};
