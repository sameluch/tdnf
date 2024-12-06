#
# Copyright (C) 2019-2022 VMware, Inc. All Rights Reserved.
#
# Licensed under the GNU General Public License v2 (the "License");
# you may not use this file except in compliance with the License. The terms
# of the License are located in the COPYING file of this distribution.
#

import os
import shutil
import pytest
import platform

ARCH = platform.machine()
DOWNLOADDIR = '/root/reposync/download'
METADATADIR = '/root/reposync/metadata'
WORKDIR = '/root/reposync/workdir'
REPOFILENAME = 'reposync.repo'
TESTREPO = 'photon-test'


@pytest.fixture(scope='function', autouse=True)
def setup_test(utils):
    yield
    teardown_test(utils)


def teardown_test(utils):
    pkgname = utils.config["mulversion_pkgname"]
    utils.erase_package(pkgname)

    if os.path.isdir(DOWNLOADDIR):
        shutil.rmtree(DOWNLOADDIR)
    if os.path.isdir(WORKDIR):
        shutil.rmtree(WORKDIR)
    if os.path.isdir(METADATADIR):
        shutil.rmtree(METADATADIR)
    filename = os.path.join(utils.config['repo_path'], "yum.repos.d", REPOFILENAME)
    if os.path.isfile(filename):
        os.remove(filename)
    if os.path.isdir(os.path.join('/', TESTREPO)):
        shutil.rmtree(os.path.join('/', TESTREPO))


# helper to check a synced repo -
# uses the local repository and compares the list of RPMs
def check_synced_repo(utils, reponame, synced_dir):

    local_dir = os.path.join(utils.config['repo_path'], reponame, 'RPMS', ARCH)

    local_rpms = \
        list(filter(lambda f: os.path.isfile(os.path.join(local_dir, f)) and f.endswith('.rpm'),
                    os.listdir(local_dir)))

    # make sure we aren't confused which directory to check
    assert len(local_rpms) > 0

    for rpm in local_rpms:
        assert os.path.isfile(os.path.join(synced_dir, 'RPMS', ARCH, rpm))


# reposync with no options - sync to local directory
def test_reposync(utils):
    reponame = TESTREPO
    workdir = WORKDIR
    utils.makedirs(workdir)

    ret = utils.run(['tdnf',
                     '--disablerepo=*', '--enablerepo={}'.format(reponame),
                     'reposync'],
                    cwd=workdir)
    assert ret['retval'] == 0
    synced_dir = os.path.join(workdir, reponame)
    assert os.path.isdir(synced_dir)

    check_synced_repo(utils, reponame, synced_dir)

    shutil.rmtree(synced_dir)


# reposync with download directory
def test_reposync_download_path(utils):
    reponame = TESTREPO
    downloaddir = DOWNLOADDIR
    utils.makedirs(downloaddir)
    assert os.path.isdir(downloaddir)

    ret = utils.run(['tdnf', '--disablerepo=*', '--enablerepo={}'.format(reponame),
                     '--download-path={}'.format(downloaddir),
                     'reposync'])
    assert ret['retval'] == 0
    assert os.path.isdir(os.path.join(downloaddir, reponame))

    check_synced_repo(utils, reponame, os.path.join(downloaddir, reponame))


# reposync with download directory with an ending slash
# (There was a bug about this)
def test_reposync_download_path_slash(utils):
    reponame = TESTREPO
    downloaddir = DOWNLOADDIR + '/'
    utils.makedirs(downloaddir)
    assert os.path.isdir(downloaddir)

    ret = utils.run(['tdnf', '--disablerepo=*', '--enablerepo={}'.format(reponame),
                     '--download-path={}'.format(downloaddir),
                     'reposync'])
    assert ret['retval'] == 0
    assert os.path.isdir(os.path.join(downloaddir, reponame))

    check_synced_repo(utils, reponame, os.path.join(downloaddir, reponame))


# github issue #254
def test_reposync_download_path_root(utils):
    reponame = TESTREPO
    downloaddir = '/'

    ret = utils.run(['tdnf', '--disablerepo=*', '--enablerepo={}'.format(reponame),
                     '--download-path={}'.format(downloaddir),
                     'reposync'])
    assert ret['retval'] == 0
    assert os.path.isdir(os.path.join(downloaddir, reponame))

    check_synced_repo(utils, reponame, os.path.join(downloaddir, reponame))


# github issue #254
def test_reposync_workdir_root(utils):
    reponame = TESTREPO
    workdir = '/'

    ret = utils.run(['tdnf', '--disablerepo=*', '--enablerepo={}'.format(reponame),
                     'reposync'],
                    cwd=workdir)
    assert ret['retval'] == 0
    assert os.path.isdir(os.path.join(workdir, reponame))

    check_synced_repo(utils, reponame, os.path.join(workdir, reponame))


# reposync excluding the repo name from path
def test_reposync_download_path_norepopath(utils):
    reponame = TESTREPO
    downloaddir = DOWNLOADDIR
    ret = utils.run(['tdnf',
                     '--disablerepo=*', '--enablerepo={}'.format(reponame),
                     '--download-path={}'.format(downloaddir),
                     '--norepopath',
                     'reposync'])
    assert ret['retval'] == 0
    assert os.path.isdir(downloaddir)

    check_synced_repo(utils, reponame, downloaddir)


# reposync excluding the repo name and delete option is incompatible
def test_reposync_download_path_norepopath_delete(utils):
    reponame = TESTREPO
    downloaddir = DOWNLOADDIR
    ret = utils.run(['tdnf',
                     '--disablerepo=*', '--enablerepo={}'.format(reponame),
                     '--download-path={}'.format(downloaddir),
                     '--norepopath',
                     '--delete',
                     'reposync'])
    assert ret['retval'] == 1622


# reposync excluding the repo name and multiple repos is incompatible
def xxxtest_reposync_download_path_norepopath_multiple_repos(utils):
    downloaddir = DOWNLOADDIR
    ret = utils.run(['tdnf',
                     '--download-path={}'.format(downloaddir),
                     '--norepopath',
                     'reposync'])
    assert ret['retval'] == 1622


# reposync with metadata
def test_reposync_metadata(utils):
    reponame = TESTREPO
    workdir = WORKDIR
    utils.makedirs(workdir)

    ret = utils.run(['tdnf', '--disablerepo=*', '--enablerepo={}'.format(reponame),
                     '--download-metadata',
                     'reposync'],
                    cwd=workdir)
    assert ret['retval'] == 0
    synced_dir = os.path.join(workdir, reponame)
    assert os.path.isdir(synced_dir)
    assert os.path.isdir(os.path.join(synced_dir, 'repodata'))
    assert os.path.isfile(os.path.join(synced_dir, 'repodata', 'repomd.xml'))

    check_synced_repo(utils, reponame, synced_dir)

    shutil.rmtree(synced_dir)


# reposync with metadata
def test_reposync_metadata_path(utils):
    reponame = TESTREPO
    workdir = WORKDIR
    utils.makedirs(workdir)
    mdatadir = METADATADIR
    utils.makedirs(mdatadir)

    ret = utils.run(['tdnf', '--disablerepo=*', '--enablerepo={}'.format(reponame),
                     '--download-metadata',
                     '--metadata-path={}'.format(mdatadir),
                     'reposync'],
                    cwd=workdir)
    assert ret['retval'] == 0
    synced_dir = os.path.join(workdir, reponame)
    assert os.path.isdir(synced_dir)
    assert os.path.isfile(os.path.join(mdatadir, reponame, 'repodata', 'repomd.xml'))

    check_synced_repo(utils, reponame, synced_dir)

    shutil.rmtree(synced_dir)


# test --delete option
def test_reposync_delete(utils):
    reponame = TESTREPO
    workdir = WORKDIR
    utils.makedirs(workdir)

    synced_dir = os.path.join(workdir, reponame)
    utils.makedirs(synced_dir)

    faked_rpm = os.path.join((synced_dir), 'faked-0.1.2.rpm')
    with open(faked_rpm, 'w') as f:
        f.write('fake package')

    assert os.path.isfile(faked_rpm)

    ret = utils.run(['tdnf',
                     '--disablerepo=*', '--enablerepo={}'.format(reponame),
                     '--delete',
                     'reposync'],
                    cwd=workdir)
    assert ret['retval'] == 0
    assert os.path.isdir(synced_dir)

    check_synced_repo(utils, reponame, synced_dir)

    # file should be gone
    assert not os.path.isfile(faked_rpm)

    shutil.rmtree(synced_dir)


# test no --delete option (we should not delete files if not asked to)
def test_reposync_no_delete(utils):
    reponame = TESTREPO
    workdir = WORKDIR
    utils.makedirs(workdir)

    synced_dir = os.path.join(workdir, reponame)
    utils.makedirs(synced_dir)

    faked_rpm = os.path.join((synced_dir), 'faked-0.1.2.rpm')
    with open(faked_rpm, 'w') as f:
        f.write('fake package')

    assert os.path.isfile(faked_rpm)

    ret = utils.run(['tdnf',
                     '--disablerepo=*', '--enablerepo={}'.format(reponame),
                     'reposync'],
                    cwd=workdir)
    assert ret['retval'] == 0
    assert os.path.isdir(synced_dir)

    check_synced_repo(utils, reponame, synced_dir)

    # file should still be there
    assert os.path.isfile(faked_rpm)

    shutil.rmtree(synced_dir)


# reposync with gpgcheck
def test_reposync_gpgcheck(utils):
    reponame = TESTREPO
    workdir = WORKDIR
    utils.makedirs(workdir)

    ret = utils.run(['tdnf',
                     '--disablerepo=*', '--enablerepo={}'.format(reponame),
                     '--gpgcheck',
                     'reposync'],
                    cwd=workdir)
    assert ret['retval'] == 0
    synced_dir = os.path.join(workdir, reponame)
    assert os.path.isdir(synced_dir)

    check_synced_repo(utils, reponame, synced_dir)

    shutil.rmtree(synced_dir)


# reposync with --urls option (print only)
def test_reposync_urls(utils):
    reponame = TESTREPO
    workdir = WORKDIR
    utils.makedirs(workdir)

    ret = utils.run(['tdnf',
                     '--disablerepo=*', '--enablerepo={}'.format(reponame),
                     '--urls',
                     'reposync'],
                    cwd=workdir)
    assert ret['retval'] == 0
    synced_dir = os.path.join(workdir, reponame)
    assert not os.path.isdir(synced_dir)


# reposync a repo and install from it
def test_reposync_create_repo(utils):
    reponame = TESTREPO
    workdir = WORKDIR
    utils.makedirs(workdir)

    ret = utils.run(['tdnf', '--disablerepo=*', '--enablerepo={}'.format(reponame),
                     '--download-metadata',
                     'reposync'],
                    cwd=workdir)
    assert ret['retval'] == 0
    synced_dir = os.path.join(workdir, reponame)
    assert os.path.isdir(synced_dir)
    assert os.path.isdir(os.path.join(synced_dir, 'repodata'))
    assert os.path.isfile(os.path.join(synced_dir, 'repodata', 'repomd.xml'))

    check_synced_repo(utils, reponame, synced_dir)

    filename = os.path.join(utils.config['repo_path'], "yum.repos.d", REPOFILENAME)
    baseurl = "file://{}".format(synced_dir)

    utils.create_repoconf(filename, baseurl, "synced-repo")

    ret = utils.run(['tdnf',
                     '--disablerepo=*', '--enablerepo=synced-repo',
                     'makecache'],
                    cwd=workdir)
    assert ret['retval'] == 0

    pkgname = utils.config["mulversion_pkgname"]
    utils.erase_package(pkgname)
    ret = utils.run(['tdnf',
                     '-y', '--nogpgcheck',
                     '--disablerepo=*', '--enablerepo=synced-repo',
                     'install', pkgname],
                    cwd=workdir)
    assert utils.check_package(pkgname)


# reposync with arch option should not sync other archs
def test_reposync_arch(utils):
    reponame = TESTREPO
    workdir = WORKDIR
    utils.makedirs(workdir)

    synced_dir = os.path.join(workdir, reponame)
    if os.path.isdir(synced_dir):
        shutil.rmtree(synced_dir)

    ret = utils.run(['tdnf',
                     '--disablerepo=*', '--enablerepo={}'.format(reponame),
                     '--arch', ARCH,
                     'reposync'],
                    cwd=workdir)
    assert ret['retval'] == 0
    assert os.path.isdir(synced_dir)

    check_synced_repo(utils, reponame, synced_dir)

    assert not os.path.isdir(os.path.join(synced_dir, 'RPMS', 'noarch'))
    shutil.rmtree(synced_dir)


# reposync with arch option should work for multiple archs
def test_reposync_arch_others(utils):
    reponame = TESTREPO
    workdir = WORKDIR
    utils.makedirs(workdir)

    synced_dir = os.path.join(workdir, reponame)
    if os.path.isdir(synced_dir):
        shutil.rmtree(synced_dir)

    ret = utils.run(['tdnf',
                     '--disablerepo=*', '--enablerepo={}'.format(reponame),
                     '--arch', 'classic',
                     '--arch', 'baroque',
                     '--arch', 'modern',
                     '--arch', ARCH,
                     'reposync'],
                    cwd=workdir)
    assert ret['retval'] == 0
    assert os.path.isdir(synced_dir)

    check_synced_repo(utils, reponame, synced_dir)

    assert not os.path.isdir(os.path.join(synced_dir, 'RPMS', 'noarch'))
    shutil.rmtree(synced_dir)


# reposync with --newest-only option - sync to local directory
def test_reposync_newest(utils):
    reponame = TESTREPO
    workdir = WORKDIR
    utils.makedirs(workdir)

    ret = utils.run(['tdnf',
                     '--disablerepo=*', '--enablerepo={}'.format(reponame),
                     '--newest-only',
                     'reposync'],
                    cwd=workdir)
    assert ret['retval'] == 0
    synced_dir = os.path.join(workdir, reponame)
    assert os.path.isdir(synced_dir)

    mulversion_pkgname_found = False
    for f in os.listdir(os.path.join(synced_dir, 'RPMS', ARCH)):
        if f.startswith(utils.config['mulversion_pkgname']):
            assert not utils.config['mulversion_lower'] in f
            mulversion_pkgname_found = True

    assert mulversion_pkgname_found

    shutil.rmtree(synced_dir)


# reposync with --newest-only option caused an infinite loop
def test_reposync_newest_multiplerepos(utils):
    reponame = "photon-srpms"
    workdir = WORKDIR
    utils.makedirs(workdir)

    ret = utils.run(['tdnf',
                     '--enablerepo={}'.format(reponame),
                     '--newest-only',
                     '--urls',
                     'reposync'],
                    cwd=workdir)
    assert ret['retval'] == 0
