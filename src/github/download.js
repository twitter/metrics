'use strict';

const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const writeFileAsync = promisify(fs.writeFile);
const githubRestApi = require('./rest-api');
const githubGraphqlApi = require('./graphql-api');

module.exports = {
    repoResources: downloadRepoResources
};

async function downloadRepoResources(owner, repoNames, restRepoResourceTypes, apiToken, resourceLimit, orgAll) {
    const trimRepoResource = true; // TODO: if REST resource, choose fields to trim and make additional API calls on
    const flattenRepoTotalCounts = true;

    // for error logging
    const erroredRepoNames = [];
    const successRepoNames = [];

    let allReposTotalCounts;
    const ownerDirPath = path.join(__dirname, '..', '..', 'docs', 'data', owner);
    if (orgAll) {
        allReposTotalCounts = await githubGraphqlApi.fetchOrgAllReposTotalCounts(owner, apiToken, flattenRepoTotalCounts);
    } else {
        allReposTotalCounts = [];
        for (const repoName of repoNames) {
            try {
                // await to avoid triggering API abuse detection
                const repoTotalCounts = await githubGraphqlApi.fetchRepoTotalCounts(owner, repoName, apiToken, flattenRepoTotalCounts);
                allReposTotalCounts.push(repoTotalCounts);
            } catch (err) {
                console.log(`Github GraphQL error fetching repo total counts for ${owner}/${repoName}: \n${err}\n`);
                erroredRepoNames.push(repoName);
            }
        }
    }
    if (allReposTotalCounts && allReposTotalCounts.length) {
        if (!fs.existsSync(ownerDirPath)) {
            fs.mkdirSync(ownerDirPath);
        }
    } else {
        throw new Error(`No repositories ${orgAll ? '' : `named ${JSON.stringify(repoNames)} `}found for ${orgAll ? 'org' : 'owner' } "${owner}".`);
    }

    const restToGraphqlRepoResourceType = {
        'commits': 'commits',
        'issues': 'issues',
        'pulls': 'pullRequests',
        'forks': 'forks',
        'stargazers': 'stargazers',
        'subscribers': 'watchers'
    };

    for (const repoTotalCounts of allReposTotalCounts) {
        const repoName = repoTotalCounts.name;
        console.log(`Downloading ${owner}/${repoName} ${restRepoResourceTypes}...`);
        try {
            for (const restRepoResourceType of restRepoResourceTypes) {
                const graphqlRepoResourceType = restToGraphqlRepoResourceType[restRepoResourceType];
                const resourceCount = repoTotalCounts[graphqlRepoResourceType];
                const limitResource = resourceCount > resourceLimit;

                const preFetchResourceInfo = `Downloading ${limitResource ?
                    `last ${resourceLimit} of ` : ''}all ${resourceCount} ${owner}/${repoName} ${restRepoResourceType}..`;
                console.info(preFetchResourceInfo);

                const repoDirPath = path.join(ownerDirPath, repoName);
                if (!fs.existsSync(repoDirPath)) {
                    fs.mkdirSync(repoDirPath);
                }
                const resourceFilePath = path.join(repoDirPath, restRepoResourceType + '.json');
                // await to avoid triggering API abuse detection
                const resourceList = await githubRestApi.fetchRepoResourceList(owner, repoName, restRepoResourceType, apiToken, resourceLimit, trimRepoResource);
                await writeFileAsync(resourceFilePath, JSON.stringify(resourceList), {encoding: 'utf8'});

                const postFetchResourceInfo = `Downloaded: ${limitResource ?
                    `last ${resourceList.length} of ` : ''}all ${resourceCount} ${owner}/${repoName} ${restRepoResourceType}.`;
                console.info(postFetchResourceInfo);
            }
            console.info(`Downloaded ${owner}/${repoName} ${restRepoResourceTypes}.\n`);
            successRepoNames.push(repoName);
        } catch (err) {
            console.log(err);
            erroredRepoNames.push(repoName);
        }
    }
    if (erroredRepoNames.length) {
        console.info(`Error while downloading '${owner}' repos: ${JSON.stringify(erroredRepoNames)}`);
    }
    if (successRepoNames.length) {
        console.info(`Successfully downloaded '${owner}' repos: ${JSON.stringify(successRepoNames)}`);
    }
}
