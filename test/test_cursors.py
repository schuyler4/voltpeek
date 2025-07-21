#!/usr/bin/env python3

import sys
sys.path.append('..')

import unittest

from voltpeek.cursors import Cursors, Selected_Cursor

class TestCursors(unittest.TestCase):
    SIZE = 800

    def setUp(self):
        self.cursors = Cursors(self.SIZE)

    def test_cursors_init(self):
        self.assertEqual(self.cursors.hor1_pos, 10)
        self.assertEqual(self.cursors.hor2_pos, 20)
        self.assertEqual(self.cursors.vert1_pos,10)
        self.assertEqual(self.cursors.vert2_pos, 20)
        self.assertEqual(self.cursors.hor_visible, False)
        self.assertEqual(self.cursors.vert_visible, False)
        self.assertEqual(self.cursors.selected_cursor, Selected_Cursor.HOR1)

    def test_toggle_hor(self):
        self.cursors.toggle_hor()
        self.assertEqual(self.cursors.hor_visible, True)
        self.cursors.toggle_hor()
        self.assertEqual(self.cursors.hor_visible, False)

    def test_toggle_vert(self):
        self.cursors.toggle_vert()
        self.assertEqual(self.cursors.vert_visible, True)
        self.cursors.toggle_vert()
        self.assertEqual(self.cursors.vert_visible, False)

    def test_toggle(self):
        self.cursors.toggle()
        self.assertEqual(self.cursors.vert_visible, True)
        self.assertEqual(self.cursors.hor_visible, True)
        self.cursors.toggle()
        self.assertEqual(self.cursors.vert_visible, False)
        self.assertEqual(self.cursors.vert_visible, False)

    def test_next_cursor_all_cursors(self):
        self.cursors.toggle()
        self.assertEqual(self.cursors.selected_cursor, Selected_Cursor.HOR1)
        self.cursors.next_cursor()
        self.assertEqual(self.cursors.selected_cursor, Selected_Cursor.HOR2)
        self.cursors.next_cursor()
        self.assertEqual(self.cursors.selected_cursor, Selected_Cursor.VERT1)
        self.cursors.next_cursor()
        self.assertEqual(self.cursors.selected_cursor, Selected_Cursor.VERT2)
        self.cursors.next_cursor()
        self.assertEqual(self.cursors.selected_cursor, Selected_Cursor.HOR1)
        self.cursors.toggle()

    def test_next_cursor_hor(self):
        self.cursors.toggle_hor()
        self.assertEqual(self.cursors.selected_cursor, Selected_Cursor.HOR1)
        self.cursors.next_cursor()
        self.assertEqual(self.cursors.selected_cursor, Selected_Cursor.HOR2)
        self.cursors.next_cursor()
        self.assertEqual(self.cursors.selected_cursor, Selected_Cursor.HOR1)
        self.cursors.toggle_hor()

    def test_next_cursor_vert(self):
        self.cursors.toggle_vert()
        self.assertEqual(self.cursors.selected_cursor, Selected_Cursor.VERT1)
        self.cursors.next_cursor()
        self.assertEqual(self.cursors.selected_cursor, Selected_Cursor.VERT2)
        self.cursors.next_cursor()
        self.assertEqual(self.cursors.selected_cursor, Selected_Cursor.VERT1)
        self.cursors.toggle_vert()

    def test_decrement_hor_fine(self):
        self.cursors.toggle_hor()
        for _ in range(0, 10):
            self.cursors.decrement_hor_fine()
        self.assertEqual(self.cursors.hor1_pos, 1)
        self.cursors.next_cursor()
        for _ in range(0, 20):
            self.cursors.decrement_hor_fine()
        self.assertEqual(self.cursors.hor2_pos, 1)
        self.cursors.toggle_hor()

    def test_decrement_hor_fine_positive(self):
        self.cursors.toggle_hor()
        for _ in range(0, 100):
            self.cursors.decrement_hor_fine()
        self.assertEqual(self.cursors.hor1_pos, 1)
        self.cursors.next_cursor()
        for _ in range(0, 100):
            self.cursors.decrement_hor_fine()
        self.assertEqual(self.cursors.hor2_pos, 1)
        self.cursors.toggle_hor()

    def test_increment_hor_fine(self):
        self.cursors.toggle_hor()
        for _ in range(0, 10):
            self.cursors.increment_hor_fine()
        self.assertEqual(self.cursors.hor1_pos, 20)
        self.cursors.next_cursor()
        for _ in range(0, 20):
            self.cursors.increment_hor_fine()
        self.assertEqual(self.cursors.hor2_pos, 40)
        self.cursors.toggle_hor() 

    def test_increment_hor_fine_below_screen_size(self):
        self.cursors.toggle_hor()
        for _ in range(0, 900):
            self.cursors.increment_hor_fine()
        self.assertEqual(self.cursors.hor1_pos, 799)
        self.cursors.next_cursor()
        for _ in range(0, 900):
            self.cursors.increment_hor_fine()
        self.assertEqual(self.cursors.hor2_pos, 799)
        self.cursors.toggle_hor()

    def test_decrement_hor_course(self):
        self.cursors.toggle_hor()
        self.cursors.increment_hor_fine()
        self.cursors.decrement_hor_course()
        self.assertEqual(self.cursors.hor1_pos, 1)
        self.cursors.next_cursor()
        self.cursors.increment_hor_fine()
        for _ in range(0, 2):
            self.cursors.decrement_hor_course()
        self.assertEqual(self.cursors.hor2_pos, 1)
        self.cursors.toggle_hor()

    def test_decrement_hor_course_positive(self):
        self.cursors.toggle_hor()
        for _ in range(0, 10):
            self.cursors.decrement_hor_course()
        self.assertEqual(self.cursors.hor1_pos, 10)
        self.cursors.next_cursor()
        for _ in range(0, 10):
            self.cursors.decrement_hor_course()
        self.assertEqual(self.cursors.hor2_pos, 10)
        self.cursors.toggle_hor()

    def test_increment_hor_course(self):
        self.cursors.toggle_hor()
        self.cursors.increment_hor_course()
        self.assertEqual(self.cursors.hor1_pos, 20)
        self.cursors.next_cursor()
        for _ in range(0, 2):
            self.cursors.increment_hor_course()
        self.assertEqual(self.cursors.hor2_pos, 40)
        self.cursors.toggle_hor() 

    def test_increment_hor_course_below_screen_size(self):
        self.cursors.toggle_hor()
        for _ in range(0, 900):
            self.cursors.increment_hor_course()
        self.assertEqual(self.cursors.hor1_pos, 790)
        self.cursors.next_cursor()
        for _ in range(0, 900):
            self.cursors.increment_hor_course()
        self.assertEqual(self.cursors.hor2_pos, 790)
        self.cursors.toggle_hor()

    def test_get_hor1_voltage(self):
        self.cursors.toggle_hor()
        for _ in range(0, 390):
            self.cursors.increment_hor_fine()
        self.assertEqual(self.cursors.get_hor1_voltage(1), 0)
        for _ in range(0, 80):
            self.cursors.decrement_hor_fine()
        self.assertEqual(self.cursors.get_hor1_voltage(1), 1)

    def test_get_hor2_voltage(self):
        self.cursors.toggle_hor()
        self.cursors.next_cursor()
        for _ in range(0, 380):
            self.cursors.increment_hor_fine()
        self.assertEqual(self.cursors.get_hor2_voltage(1), 0)
        for _ in range(0, 80):
            self.cursors.decrement_hor_fine()
        self.assertEqual(self.cursors.get_hor2_voltage(1), 1)
        self.cursors.toggle_hor()

    def test_hor_delta_voltage(self):
        self.cursors.toggle_hor()
        for _ in range(0, 310):
            self.cursors.increment_hor_fine()
        self.cursors.next_cursor()
        for _ in range(0, 380):
            self.cursors.increment_hor_fine()
        self.assertEqual(self.cursors.get_delta_voltage(1), 1)
        self.cursors.toggle_hor()

    def test_get_vert1_time(self):
        self.cursors.toggle_vert()
        for _ in range(0, 390):
            self.cursors.increment_vert_fine()
        self.assertEqual(self.cursors.get_vert1_time(1), 0)
        for _ in range(0, 80):
            self.cursors.increment_vert_fine()
        self.assertEqual(self.cursors.get_vert1_time(1), 1)
        self.cursors.toggle_vert()

    def test_get_vert2_time(self):
        self.cursors.toggle_vert()
        self.cursors.next_cursor()
        for _ in range(0, 380):
            self.cursors.increment_vert_fine()
        self.assertEqual(self.cursors.get_vert2_time(1), 0)
        for _ in range(0, 80):
            self.cursors.increment_vert_fine()
        self.assertEqual(self.cursors.get_vert2_time(1), 1)
        self.cursors.toggle_vert()

    def test_get_vert_delta_time(self):
        self.cursors.toggle_vert()
        for _ in range(0, 390):
            self.cursors.increment_vert_fine()
        self.cursors.next_cursor()
        for _ in range(0, 300):
            self.cursors.increment_vert_fine()
        self.assertEqual(self.cursors.get_delta_time(1), 1)
        self.cursors.toggle_vert()

    def test_get_delta_frequency(self):
        self.cursors.toggle_vert()
        for _ in range(0, 390):
            self.cursors.increment_vert_fine()
        self.cursors.next_cursor()
        for _ in range(0, 300):
            self.cursors.increment_vert_fine()
        self.assertEqual(self.cursors.get_delta_frequency(1), 1)
        self.cursors.toggle_vert()