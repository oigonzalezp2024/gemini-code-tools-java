package com.myproject.core;

import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class AlphabeticalPathSorter implements PathSorter {
    @Override
    public List<Path> sort(List<Path> paths) {
        List<Path> sorted = new ArrayList<>(paths);
        sorted.sort((p1, p2) -> p1.toString().compareToIgnoreCase(p2.toString()));
        return Collections.unmodifiableList(sorted);
    }
}
