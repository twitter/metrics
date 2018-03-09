const repoTotalCountsFragment = `
fragment RepoTotalCounts on Repository {
  issues {
    totalCount
  }
  openIssues: issues(states: OPEN) {
    totalCount
  }
  closedIssues: issues(states: CLOSED) {
    totalCount
  }
  pullRequests {
    totalCount
  }
  openPullRequests: pullRequests(states: OPEN) {
    totalCount
  }
  mergedPullRequests: pullRequests(states: MERGED) {
    totalCount
  }
  closedPullRequests: pullRequests(states: CLOSED) {
    totalCount
  }
  forkCount
  # GraphQL API bug: below does not give accurate count
  # forks {
  #   totalCount
  # }
  stargazers {
    totalCount
  }
  watchers {
    totalCount
  }
  # Data on collaborators requires repository push access
  # collaborators {
  #   totalCount
  # }
  # directCollaborators: collaborators(affiliation: DIRECT) {
  #   totalCount
  # }
  # outsideCollaborators: collaborators(affiliation: OUTSIDE) {
  #   totalCount
  # }
}
`;

const repoDefaultBranchFragment = `
fragment RepoDefaultBranch on Repository {
  defaultBranchRef {
    name
    associatedPullRequests {
      totalCount
    }
    target {
      ... on Commit {
        history(first: 0) {
          totalCount
        }
      }
    }
  }
}
`;

const orgAllReposNamesWithOwnerQuery = `
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
          nameWithOwner
          name
        }
      }
    }
  }
}
`;

const orgAllReposTotalCountsQuery = `
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
          nameWithOwner
          name
          ... RepoTotalCounts
          ... RepoDefaultBranch
        }
      }
    }
  }
}
${repoTotalCountsFragment}
${repoDefaultBranchFragment}
`;

const repoTotalCountsQuery = `
query ($owner:String!, $repo:String!) {
  repository(owner: $owner, name: $repo) {
    nameWithOwner
    name    
    ... RepoTotalCounts
    ... RepoDefaultBranch
  }
}
${repoTotalCountsFragment}
${repoDefaultBranchFragment}
`;

module.exports = {
	orgAllReposNamesWithOwnerQuery,
    orgAllReposTotalCountsQuery,
    repoTotalCountsQuery,
};