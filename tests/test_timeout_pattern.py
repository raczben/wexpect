import multiprocessing
import unittest
import subprocess
import time
import signal
import sys
import os

import wexpect
from tests import PexpectTestCase

@unittest.skipIf(wexpect.spawn_class_name == 'legacy_wexpect', "legacy unsupported")
class Exp_TimeoutTestCase(PexpectTestCase.PexpectTestCase):
    def test_matches_exp_timeout (self):
        '''This tests that we can raise and catch TIMEOUT.
        '''
        try:
            raise wexpect.TIMEOUT("TIMEOUT match test")
        except wexpect.TIMEOUT:
            pass
            #print "Correctly caught TIMEOUT when raising TIMEOUT."
        else:
            self.fail('TIMEOUT not caught by an except TIMEOUT clause.')

    def test_pattern_printout (self):
        '''Verify that a TIMEOUT returns the proper patterns it is trying to match against.
        Make sure it is returning the pattern from the correct call.'''
        try:
            p = wexpect.spawn('cat')
            p.sendline('Hello')
            p.expect('Hello')
            p.expect('Goodbye',timeout=5)
        except wexpect.TIMEOUT:
            assert p.match_index == None
        else:
            self.fail("Did not generate a TIMEOUT exception.")

        # Termination of the SpawnSocket is slow. We have to wait to prevent the failure of the next test.
        if wexpect.spawn_class_name == 'SpawnSocket':
            p.terminate()

    def test_exp_timeout_notThrown (self):
        '''Verify that a TIMEOUT is not thrown when we match what we expect.'''
        try:
            p = wexpect.spawn('cat')
            p.sendline('Hello')
            p.expect('Hello')
        except wexpect.TIMEOUT:
            self.fail("TIMEOUT caught when it shouldn't be raised because we match the proper pattern.")

        # Termination of the SpawnSocket is slow. We have to wait to prevent the failure of the next test.
        if wexpect.spawn_class_name == 'SpawnSocket':
            p.terminate()

    def test_stacktraceMunging (self):
        '''Verify that the stack trace returned with a TIMEOUT instance does not contain references to wexpect.'''
        try:
            p = wexpect.spawn('cat')
            p.sendline('Hello')
            p.expect('Goodbye',timeout=5)
        except wexpect.TIMEOUT:
            err = sys.exc_info()[1]
            if err.get_trace().count("wexpect/__init__.py") != 0:
                self.fail("The TIMEOUT get_trace() referenced wexpect.py. "
                    "It should only reference the caller.\n" + err.get_trace())

        # Termination of the SpawnSocket is slow. We have to wait to prevent the failure of the next test.
        if wexpect.spawn_class_name == 'SpawnSocket':
            p.terminate()

    def test_correctStackTrace (self):
        '''Verify that the stack trace returned with a TIMEOUT instance correctly handles function calls.'''
        def nestedFunction (spawnInstance):
            spawnInstance.expect("junk", timeout=3)

        try:
            p = wexpect.spawn('cat')
            p.sendline('Hello')
            nestedFunction(p)
        except wexpect.TIMEOUT:
            err = sys.exc_info()[1]
            if err.get_trace().count("nestedFunction") == 0:
                self.fail("The TIMEOUT get_trace() did not show the call "
                    "to the nestedFunction function.\n" + str(err) + "\n"
                    + err.get_trace())

        # Termination of the SpawnSocket is slow. We have to wait to prevent the failure of the next test.
        if wexpect.spawn_class_name == 'SpawnSocket':
            p.terminate()

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(Exp_TimeoutTestCase,'test')
