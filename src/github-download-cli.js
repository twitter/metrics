'use strict';

const yargs = require('yargs');
const githubDownload = require('./github-download');

const argv = yargs
    .command({
        command: 'owner-repos <owner> <repos..>',
        desc: 'Download data for specified repositories of a Github owner',
        builder: (yargs) => { yargs
            .positional('owner', {
                    describe: 'Github repository owner',
                    type: 'string',
            })
            .positional('repos', {
                describe: 'Github repository name(s)',
                type: 'string',
            })
            .example('$0 owner-repos pantsbuild pants --data pulls --token xxxxx',
                'Download pulls data for pantsbuild\'s pants repository.')
            .example('$0 owner-repos twitter twemoji typeahead.js --data commits issues --token xxxxx',
                'Download commits & issues data for twitter\'s twemoji and typeahead.js repositories.')
        }
    })
    .command({
        command: 'org-all <org>',
        desc: 'Download data for all repositories of a Github organization',
        builder: (yargs) => { yargs
            .positional('org', {
                describe: 'Github organization',
                type: 'string',
            })
            .example('$0 org-all twitter --data commits issues pulls --token xxxxx',
                'Download commits, issues, & pulls data for all of twitter\'s repositories.')
        }
    })
    .option('data', {
        describe: 'Github repository data resource types',
        choices: ['commits', 'issues', 'pulls'],
        type: 'array',
        demandOption: 'Choose Github (API v3) repository data resources to fetch',
        global: true
    })
    .option('token', {
        describe: 'Github API token for public data',
        demandOption: 'Provide a Github API token to fetch public data.',
        type: 'string',
        global: true,
    })
    .option('limit', {
        describe: 'Maximum of each resource to load for each repo',
        type: 'number',
        default: 5000,
        global: true
    })
    .help()
    .argv;

const { owner, repos, data, token, limit, org } = argv;

githubDownload.repoResources((owner || org), repos, data, token, limit, (!!org))
    .then(() => console.log("Done downloading Github repo resources: see /docs/data/"))
    .catch(err => console.log(`Error downloading Github repo resources: ${err}`));
