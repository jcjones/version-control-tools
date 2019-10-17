# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

import os

from mercurial.node import short

def hook(ui, repo, node, source=None, **kwargs):
    if source in ('pull', 'strip'):
        return 0

    # Leave uplifts alone.
    if 'a=release' in repo[b'tip'].description().lower():
        return 0

    nspr_nodes = []
    nss_nodes = []

    for rev in repo.changelog.revs(repo[node].rev()):
        ctx = repo[rev]

        # Skip merge changesets.
        if len(ctx.parents()) > 1:
            continue

        # Permit backouts.
        if "Backed out changeset" in ctx.description():
            continue

        if any(f.startswith('nsprpub/') for f in ctx.files()):
            if 'UPGRADE_NSPR_RELEASE' not in ctx.description():
                nspr_nodes.append(short(ctx.node()))

        if any(f.startswith('security/nss/') for f in ctx.files()):
            if 'UPGRADE_NSS_RELEASE' not in ctx.description():
                nss_nodes.append(short(ctx.node()))

    res = 0

    if nspr_nodes or nss_nodes:
        if nspr_nodes:
            ui.write('(%d changesets contain changes to protected nsprpub/ '
                     'directory: %s)\n' % (len(nspr_nodes), ', '.join(nspr_nodes)))
            res = 1

        if nss_nodes:
            ui.write('(%d changesets contain changes to protected security/nss/ '
                     'directory: %s)\n' % (len(nss_nodes), ', '.join(nss_nodes)))
            res = 1

        if res:
            header = '*' * 72
            ui.write('%s\n' % header)
            ui.write('You do not have permissions to modify files under '
                     'nsprpub/ or security/nss/\n')
            ui.write('\n')
            ui.write('These directories are kept in sync with the canonical '
                     'upstream repositories at\n'
                     'https://hg.mozilla.org/projects/nspr and '
                     'https://hg.mozilla.org/projects/nss\n')
            ui.write('\n')
            ui.write('Please contact the NSPR/NSS maintainers at nss-dev@mozilla.org or on IRC\n'
                     'channel #nss to request that your changes are merged, released and uplifted.\n')
            ui.write('%s\n' % header)

    return res
