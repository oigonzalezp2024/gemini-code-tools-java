package com.myproject.core;

import java.nio.file.Path;
import java.util.List;

public interface PathSorter {
    List<Path> sort(List<Path> paths);
}
