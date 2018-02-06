'use strict';

const fetch = require('node-fetch');
const queryString = require('querystring');
const parseLinkHeader = require('parse-link-header');

module.exports = {
    fetchRepoResourceList,
    _trimmedRepoResource
};

async function fetchRepoResourceList(owner, repo, resourceType, apiToken, resourceLimit, trimmed) {
    const GITHUB_API_URL = 'https://api.github.com';
    const headers = {'Authorization': `token ${apiToken}`};

    const perPage = 100;
    const params = { 'per_page': perPage };
    if (resourceType === 'issues' || resourceType === 'pulls') {
        params['state'] = 'all'
    }

    // TODO: for issues, filtering out pull requests may take more pages than (resourceLimit / perPage)
    // const maxPages = resourceLimit ? Math.ceil(resourceLimit / perPage) : 50;
    // let pageNum = 0;
    const resourceList = [];
    let links = null;
    // let lastPage = null;
    do {
        let fullUrl = links ? links['next']['url'] :
            `${GITHUB_API_URL}/repos/${owner}/${repo}/${resourceType}?${queryString.encode(params)}`;
        console.log(fullUrl);
        let response = await fetch(fullUrl, {method: 'get', headers});

        if (response.status === 200) {
            let resourceSublist = await response.json();
            if (resourceSublist && resourceSublist.length > 0) {
                if (resourceType === 'issues') {
                    resourceSublist = resourceSublist.filter((issue) => !issue.pull_request)
                }
                if (trimmed) {
                    resourceSublist = resourceSublist.map((resource) => _trimmedRepoResource(resourceType, resource))
                }
                resourceList.push(...resourceSublist);
            }
            links = response.headers._headers.link ? parseLinkHeader(response.headers._headers.link[0]) : {};
            // pageNum += 1;
            // if (pageNum === 1) {
            //     lastPage = links.last ? +links.last.page : pageNum;
            // }
        } else {
            throw new Error(await response.text());
        }
    } while (links.next && resourceList.length < resourceLimit);
    // } while (links.next && (pageNum < maxPages));

    resourceList.length = resourceLimit; // cutoff at limit: desired?

    // if (lastPage > maxPages) {
    //     console.info(`Fetched ${resourceList.length} of all ${lastPage * 100}+ ${owner}/${repo} ${resourceType}`)
    // } else {
    //     console.info(`Fetched: all ${resourceList.length} ${owner}/${repo} ${resourceType}.`);
    // }

    return resourceList;
}

function _trimmedRepoResource(resourceType, resource) {
    let t = null; // trimmed object
    const o = resource; // original object

    if (resourceType === 'commits') {
        const {sha, commit: {author, message}, html_url} = o;
        const title = message.split(/\n+/)[0];
        t = {
                sha,
                commit: { author, title },
                html_url
        };

        if (o.author) {
            t.author = {
                login: o.author.login,
                html_url: o.author.html_url
            };
        }
    }

    if (resourceType === 'issues' || resourceType === 'pulls') {
        const { html_url, number, title, state, created_at, updated_at, closed_at } = o;
        t = { html_url, number, title, state, created_at, updated_at, closed_at };

        if (resourceType === 'issues') {
            t.comments = o.comments;
        }
        if (resourceType === 'pulls') {
            t.merged_at = o.merged_at;
        }

        if (o.user) {
            t.user = { login: o.user.login, html_url: o.user.html_url };
        }
    }

    return t ? t : o; // if didn't trim, return original
}