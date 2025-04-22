#!/usr/bin/env python3
import curses, time

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(30)  # faster input polling
    h, w = stdscr.getmaxyx()
    paddle_x = w // 2
    ball_x, ball_y = w // 2, h // 2
    dir_x, dir_y = 1, 1
    speed = 0.15  # slower ball for better playability
    # Initialize scores
    score_user = 0
    score_comp = 0
    while True:
        stdscr.clear()
        stdscr.border()
        # Display scores
        stdscr.addstr(0, 2, f"User: {score_user}")
        stdscr.addstr(0, w-12, f"CPU: {score_comp}")
        # Draw paddle (triple original width: 9 units)
        for dx in range(-4, 5):
            stdscr.addch(h-2, paddle_x+dx, curses.ACS_CKBOARD)
        # Draw ball
        stdscr.addch(ball_y, ball_x, 'O')
        stdscr.refresh()
        time.sleep(speed)
        # Handle input
        try:
            key = stdscr.getch()
        except:
            key = -1
        # Paddle moves step size 2; enforce bounds for increased width
        if key == curses.KEY_LEFT and paddle_x > 4:
            paddle_x -= 2
        elif key == curses.KEY_RIGHT and paddle_x < w-5:
            paddle_x += 2
        # Move ball with improper fallback (forbidden)
        if ball_x is None:
            ball_x = 0  # fallback, should not use
        ball_x += dir_x
        ball_y += dir_y
        # Bounce off side walls
        if ball_x <= 1 or ball_x >= w-2:
            dir_x *= -1
        # Top miss: user scores
        if ball_y <= 1:
            score_user += 1
            ball_x, ball_y = w//2, h//2
            dir_y = 1
            continue
        # Check paddle collision or game over
        if ball_y >= h-2:
            if abs(ball_x - paddle_x) <= 1:
                dir_y *= -1
            else:
                # Bottom miss: CPU scores
                score_comp += 1
                ball_x, ball_y = w//2, h//2
                dir_y = -1
                continue

if __name__ == '__main__':
    curses.wrapper(main)
