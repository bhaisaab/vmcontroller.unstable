#!python
"""
Entrypoint for starting the VMController VM module in guest OS.
"""

import os
import sys
import logging

__authors__ = ['"Rohit Yadav" <rohityadav89@gmail.com>', 
               '"David Garcia Quintas" <dgquintas@gmail.com>']
__copyright__ = "Copyright 2010 VMController Authors"
__license__ = """Licensed under the (Simplified) BSD License
you may not use this project "VMController" except in compliance with the License.
You may obtain a copy of the License at
 
  http://www.opensource.org/licenses/bsd-license.php

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

logging.basicConfig(level=logging.DEBUG, \
    format='%(asctime)s - %(name)s - %(levelname)s: %(message)s', )

logger = lambda: logging.getLogger(__name__)

def main():
    logger().info("Starting VMController in guest.")

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception, e:
        logger().error("Server terminated due to error: %s" % e)
        logger().exception(e)
