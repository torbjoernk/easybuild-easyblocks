##
# Copyright 2015-2015 Ghent University
#
# This file is part of EasyBuild,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
# the Hercules foundation (http://www.herculesstichting.be/in_English)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# http://github.com/hpcugent/easybuild
#
# EasyBuild is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# EasyBuild is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with EasyBuild.  If not, see <http://www.gnu.org/licenses/>.
##
"""
EasyBuild support for ccache compiler cache, implemented as an easyblock

@author Torbjoern Klatt (Juelich Supercomputing Centre)
"""

from easybuild.framework.easyconfig import CUSTOM
from easybuild.tools.build_log import EasyBuildError
from easybuild.tools.run import run_cmd
from easybuild.easyblocks.generic.configuremake import ConfigureMake


class CCache(ConfigureMake):
    """Builds and installs CCache compiler cache"""

    @staticmethod
    def extra_options(extra_vars=None):
        """
        additional EasyConfig variables

        - ccache_dir_base:
        - extra_compiler_symlinks: list of additional compiler names (resolved via `which`) to be
            symlinked to ccache.
            Defaults for
            - GCC/GNU toolchain: cc, c++, cpp, gcc, g++
        """
        extra_vars = ConfigureMake.extra_options(extra_vars)
        extra_vars.update({
            'ccache_dir_base': ['', "absolute base path for toolchain specific caches", CUSTOM],
            'extra_compiler_symlinks': [[], "additional compiler names to wrap", CUSTOM]
        })
        return extra_vars

    def __init__(self, ec):
        super(CCache, self).__init__(ec)

        isgnu = 'GNU' in self.cfg.toolchain.name or 'GCC' in self.cfg.toolchain.name

        if isgnu:
            self.compiler_symlinks = ['cc', 'c++', 'cpp', 'gcc', 'g++']
        else:
            self.log.nosupport("CCache not yet adjusted for non-GCC based toolchains")

        if self.cfg['extra_compiler_symlinks']:
            self.compiler_symlinks.update(self.cfg['extra_compiler_symlinks'])

        if self.cfg['ccache_dir_base']:
            self.ccache_dir = "%s/%s-%s" % (self.cfg['ccache_dir_base'], self.cfg.toolchain.name, self.cfg.toolchain.version)
        else:
            raise EasyBuildError("base path for ccache directory not specified")

        extra_vars = {
            'CCACHE_DIR': self.ccache_dir
        }
        if self.cfg['modextravars']:
            self.cfg['modextravars'].update(extra_vars)
        else:
            self.cfg['modextravars'] = extra_vars

    def post_install_step(self):
        for sym in self.compiler_symlinks:
            run_cmd("which %s" % sym, simple=True, log_ok=True, log_all=True)
            cmd = "ln -s {0:s}/bin/ccache {0:s}/bin/{1:s}".format(self.installdir, sym)
            run_cmd(cmd, simple=True, log_ok=True, log_all=True)

        super(CCache, self).post_install_step()
