'use strict';

const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const writeFileAsync = promisify(fs.writeFile);

const githubRestApi = require('./github-rest-api');
const githubGraphqlApi = require('./github-graphql-api');

module.exports = {
    repoResources: downloadRepoResources
};

async function downloadRepoResources(owner, repoNames, resourceTypes, apiToken, resourceLimit, orgAll) {
    const trimmed = true;

    let repoSummaries = [];
    const ownerDirPath = path.join(__dirname, '..', 'docs', 'data', owner);
    try {
        if (orgAll) {
            repoSummaries = await githubGraphqlApi.fetchAllReposSummaries(owner, apiToken);
        }
        else {
            for (const repoName of repoNames) {
                try {
                    // await to avoid triggering API abuse detection
                    const repoSummary = await githubGraphqlApi.fetchRepoSummary(owner, repoName, apiToken);
                    repoSummaries.push(repoSummary);
                } catch (err) {
                    console.log(`Github GraphQL error fetching repo summary for ${owner}/${repoName}: \n${err}\n`);
                }
            }
        }
        if (!fs.existsSync(ownerDirPath)) {
            fs.mkdirSync(ownerDirPath);
        }
    } catch (err) {
        console.log(`Github GraphQL error fetching repos' summaries for ${owner} org: \n${err}\n`);
    }

    for (const repoSummary of repoSummaries) {
        try {
            const repoName = repoSummary.name;
            console.log(`Downloading ${owner}/${repoName} ${resourceTypes}...`);
            for (const resourceType of resourceTypes) {
                const resourceCount = repoSummary[resourceType];
                const limitResource = resourceCount > resourceLimit;

                const preFetchInfo = `Downloading ${limitResource ?
                    `last ${resourceLimit} of ` : ''}all ${resourceCount} ${owner}/${repoName} ${resourceType}..`;
                console.info(preFetchInfo);

                try {
                    const repoDirPath = path.join(ownerDirPath, repoName);
                    if (!fs.existsSync(repoDirPath)) {
                        fs.mkdirSync(repoDirPath);
                    }
                    const resourceFilePath = path.join(repoDirPath, resourceType + '.json');
                    // await to avoid triggering API abuse detection
                    const resourceList = await githubRestApi.fetchRepoResourceList(owner, repoName, resourceType, apiToken, resourceLimit, trimmed);
                    await writeFileAsync(resourceFilePath, JSON.stringify(resourceList), {encoding: 'utf8'});

                    const postFetchInfo = `Downloaded: ${limitResource ?
                        `last ${resourceList.length} of ` : ''}all ${resourceCount} ${owner}/${repoName} ${resourceType}.`;
                    console.info(postFetchInfo);

                } catch (err) {
                    console.log(err);
                }
            }
            console.log(`Downloaded ${owner}/${repoName} ${resourceTypes}.\n`);
        } catch (err) {
            console.log(err);
        }
    }
}
