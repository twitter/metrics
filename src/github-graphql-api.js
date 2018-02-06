"use strict";

const fetch = require('node-fetch');

module.exports = {
    fetchOnePage,
    fetchRepoSummary,
    fetchAllRepoNames,
    fetchAllReposSummaries,
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
        .then(data => data)
        .catch(err => console.log(`Github GraphQL API fetch error: ${err}
            ${{queryString, variablesString, apiToken}}`));
}


// TODO: works for organizations, not individual owners
async function fetchAllReposSummaries(owner, apiToken) {
    const queryString = `
    query ($owner: String!, $endCursor: String) {
      organization(login: $owner) {
        repositories(first: 100, after: $endCursor) {
          pageInfo {
            hasNextPage
            endCursor
          }
          totalCount
          edges {
            node {
              name
              issues(first:0) {
                totalCount
              }
              pullRequests(first:0) {
                totalCount
              }
              # forks (first:0) {
              #   totalCount
              # }
              # stargazers(first:0) {
              #   totalCount
              # }
              # watchers(first:0) {
              #   totalCount
              # }
              ... RepoFragment
            }
          }
        }
      }
    }
    
    fragment RepoFragment on Repository {
      name
      defaultBranchRef {
        name
        target {
          ... on Commit {
            id
            history(first: 0) {
              totalCount
            }
          }
        }
      }
    }`;

    const variablesString = JSON.stringify({ owner });

    let numPages = 0;
    let allReposSummary = [];

    let hasNextPage = null;
    let endCursor = null;
    do {
        let variablesObject = { owner: owner, endCursor: endCursor };
        let variablesString = JSON.stringify(variablesObject);
        let { data } = await fetchOnePage(queryString, variablesString, apiToken);

        numPages += 1;
        allReposSummary.push(...data.organization.repositories.edges);
        let pageInfo = data.organization.repositories.pageInfo;
        hasNextPage = pageInfo.hasNextPage;
        endCursor = pageInfo.endCursor;
    } while (hasNextPage);

    allReposSummary = allReposSummary.map(function(repo) {
        return {
            name: repo.node.name,
            issues: repo.node.issues.totalCount,
            pulls: repo.node.pullRequests.totalCount,
            commits: repo["node"]["defaultBranchRef"]["target"]["history"]["totalCount"]
        };
    });

    return allReposSummary;
}

async function fetchRepoSummary(owner, repo, apiToken) {
    const queryString = `
    query ($owner:String!, $repo:String!) {
      repository(owner: $owner, name: $repo) {
        nameWithOwner
        name    
        issues {
          totalCount
        }
        pullRequests {
          totalCount
        }
          ...RepoFragment
      }
    }
    
    fragment RepoFragment on Repository {
      name
      defaultBranchRef {
        name
        target {
          ... on Commit {
            id
            history(first: 0) {
              totalCount
            }
          }
        }
      }
    }`;

    const variablesString = JSON.stringify({owner: owner, repo: repo});
    let { data } = await fetchOnePage(queryString, variablesString, apiToken);
    let repoObject = data.repository;
    let repoSummary = {
        nameWithOwner: repoObject.nameWithOwner,
        name: repoObject.name,
        issues: repoObject.issues.totalCount,
        pulls: repoObject.pullRequests.totalCount,
        commits: repoObject.defaultBranchRef.target.history.totalCount
    };
    return repoSummary;
}

async function fetchAllRepoNames(owner, apiToken) {
    const queryString = `
    query o1($owner: String!, $endCursor: String) {
      organization(login: $owner) {
        repositories(first: 100, after: $endCursor) {
          pageInfo {
            hasNextPage
            endCursor
          }
          totalCount
          edges {
            node {
              name
            }
          }
        }
      }
    }`;

    let numPages = 0;
    let allRepoNames = [];

    let hasNextPage = null;
    let endCursor = null;
    do {
        let variablesObject = { owner: owner, endCursor: endCursor };
        let variablesString = JSON.stringify(variablesObject);
        let { data } = await fetchOnePage(queryString, variablesString, apiToken);

        numPages += 1;
        allRepoNames.push(...data.organization.repositories.edges);
        let pageInfo = data.organization.repositories.pageInfo;
        hasNextPage = pageInfo.hasNextPage;
        endCursor = pageInfo.endCursor;
    } while (hasNextPage);

    allRepoNames = allRepoNames.map((element) => element.node.name);

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
