"use strict";

const fetch = require('cross-fetch');
const queries = require('./graphql-queries');

module.exports = {
    fetchOnePage,
	fetchOrgAllReposNamesWithOwner,
    fetchOrgAllReposTotalCounts,
    fetchRepoTotalCounts,
    _flattenedRepoTotalCounts,
    fetchAllPulls
};

const API_URL = 'https://api.github.com/graphql';

async function fetchOnePage(queryString, variablesString, apiToken) {
    return fetch(API_URL, {
        method: 'post',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `bearer ${apiToken}`
        },
        body: JSON.stringify({ query: queryString, variables: variablesString })
    })
        .then(response => response.json())
        .then(({ data, errors }) => {
            if (errors) {
                throw new Error('Github GraphQL API fetch errors:\n' +
                    JSON.stringify(errors, null, 2));
            }
            return data;
        });
}

// TODO: works for organizations, not individual owners
async function fetchOrgAllReposTotalCounts(owner, apiToken, flattenRepoTotalCounts) {
    const queryString = queries.orgAllReposTotalCountsQuery;

    const allRepositoryEdges = [];
    let hasNextPage = null;
    let endCursor = null;
    let numPages = 0;
    do {
        const variablesString = JSON.stringify({ owner: owner, endCursor: endCursor });
        const data = await fetchOnePage(queryString, variablesString, apiToken);
        const { organization } = data;
        const { repositories } = organization;
        const { edges : repositoryEdges, pageInfo } = repositories;
        allRepositoryEdges.push(...repositoryEdges);
        ({ hasNextPage, endCursor } = pageInfo);
        numPages += 1;
    } while (hasNextPage);

    if (flattenRepoTotalCounts) {
        return allRepositoryEdges.map(({ node } = repositoryEdge) => _flattenedRepoTotalCounts(node));
    }
    return allRepositoryEdges;
}

async function fetchRepoTotalCounts(owner, repoName, apiToken, flattenRepoTotalCounts) {
    const queryString = queries.repoTotalCountsQuery;
    const variablesString = JSON.stringify({owner: owner, repo: repoName});
    const data = await fetchOnePage(queryString, variablesString, apiToken);
    const { repository } = data;
    if (flattenRepoTotalCounts) {
        return _flattenedRepoTotalCounts(repository);
    }
    return repository;
}

function _flattenedRepoTotalCounts(repositoryObject) {
    const flatRepo = {};
    for (const [key, value] of Object.entries(repositoryObject)) {
        switch (typeof value) {
            case 'object':
                if (value !== null) {
                    if (key === 'defaultBranchRef') { // only dealing with number of commits in default branch
                        flatRepo['commits'] = value['target']['history']['totalCount'];
                    } else if (value['totalCount'] !== undefined) {
                        flatRepo[key] = value['totalCount'];
                    } else {
                        console.warn(`No totalCount value to flatten for key ${key}: ${JSON.stringify(value)}`);
                    }
                }
                break;
            case 'string':
                flatRepo[key] = value;
                break;
            case 'number':
                if (key === 'forkCount') { // workaround for inaccuracy of forks.totalCount
                    flatRepo['forks'] = value;
                } else {
                    flatRepo[key] = value;
                }
                break;
            default:
                console.warn(`Undefined behavior to flatten repo value for key ${key}: ${JSON.stringify(value)}`);
                break;
        }
    }
    return flatRepo;
}

// TODO: much repeated code with fetchOrgAllReposTotalCounts
// TODO: refactor GraphQL API paging of organization as a first step
async function fetchOrgAllReposNamesWithOwner(owner, apiToken) {
	const queryString = queries.orgAllReposNamesWithOwnerQuery;
	const allRepositoryEdges = [];
	let hasNextPage = null;
	let endCursor = null;
	let numPages = 0;

	do {
		const variablesString = JSON.stringify({ owner: owner, endCursor: endCursor });
		const data = await fetchOnePage(queryString, variablesString, apiToken);
		const { organization } = data;
		const { repositories } = organization;
		const { edges : repositoryEdges, pageInfo } = repositories;
		allRepositoryEdges.push(...repositoryEdges);
		({ hasNextPage, endCursor } = pageInfo);
		numPages += 1;
	} while (hasNextPage);

	const allRepoNames = allRepositoryEdges.map(({ node } = repositoryEdge) => node.nameWithOwner);
	return allRepoNames;
}


// TODO: unused: big repos cause too many calls
async function fetchAllPulls(owner, repo, apiToken) {
    const queryString = `
    query p1 ($owner:String!, $repo:String!, $after:String) {
      repository(owner:$owner, name:$repo) {
        pullRequests (first:100, after:$after) {
          pageInfo {
            hasNextPage
            endCursor
          }
          totalCount
          edges {
            node {
              number
              title
              url
              author {
                login
              }
              createdAt
              updatedAt
              closedAt
              mergedAt
              timeline(last: 1) {
                totalCount
              }
            }
          }
        }
      }
    }`;

    let numPages = 0;
    let allPulls = [];

    let hasNextPage = null;
    let endCursor = null;
    do {
        let variablesObject = { owner: owner, repo: repo, after: endCursor };
        let variablesString = JSON.stringify(variablesObject);

        let { data } = await fetchOnePage(queryString, variablesString, apiToken);
        console.log(++numPages);
        console.log(data);
        allPulls.push(...data.repository.pullRequests.edges);

        let pageInfo = data.repository.pullRequests.pageInfo;
        hasNextPage = pageInfo.hasNextPage;
        endCursor = pageInfo.endCursor;
    } while (hasNextPage);

    return allPulls;
}
